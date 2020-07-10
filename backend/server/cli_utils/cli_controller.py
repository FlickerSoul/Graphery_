import json
import pathlib
import re
import time
import shutil
from importlib import import_module
from typing import Tuple, List, MutableMapping, Sequence
from html.parser import HTMLParser

from django.db.models import QuerySet
from django.db.transaction import commit, rollback

from prompt_toolkit.completion import PathCompleter
from prompt_toolkit import print_formatted_text, prompt
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.document import Document

import markdown

from backend.model.translation_collection import translation_table_mapping, get_translation_table
from cli_utils.cli_ui import run_interruptable_checkbox_dialog, new_session, inline_radio_dialog
from bundle.controller import controller
from bundle.utils.cache_file_helpers import TempSysPathAdder
from bundle.GraphObjects.Graph import Graph as CustomGraph
from .errors import InvalidGraphJson

from .intel_wrapper import *


class CustomHtmlParser(HTMLParser):
    def error(self, message):
        raise ValueError(message)

    def __init__(self):
        super().__init__()
        self.first: bool = True
        self.recording: bool = False
        self.data: List = []

    def handle_starttag(self, tag, attrs):
        if self.first and tag == 'p':
            self.first = False
            self.recording = True

    def handle_endtag(self, tag):
        if self.recording and tag == 'p':
            self.recording = False

    def handle_data(self, data):
        if self.recording:
            self.data.append(data)


class CodeSourceFolderValidator(Validator):
    def validate(self, document: Document) -> None:
        code_path = pathlib.Path(document.text)
        entry_py_module = code_path / 'entry.py'
        graph_info = code_path / 'graph-info.json'
        if not code_path.exists() or not entry_py_module.exists() or not graph_info.exists():
            raise ValidationError(message='The code resources folder does not exist or does not contain'
                                          ' an `entry.py` file and a `graph-info.json` file.')


_code_source_folder_validator = CodeSourceFolderValidator()


class TutorialSourceFolderValidator(Validator):
    def validate(self, document: Document) -> None:
        path = pathlib.Path(document.text)
        graph_path = path / 'graphs'
        locale_path = path / 'locale'
        # ehhhhhh
        _code_source_folder_validator.validate(Document(text=(path / 'codes').absolute()))
        if not (path.exists() and graph_path.exists() and locale_path.exists()):
            raise ValidationError(message='The tutorial source file folder structure is not right')


class NameValidator(Validator):
    regex = re.compile(r'^[a-zA-Z0-9- ]+\Z')

    def __init__(self):
        super().__init__()
        self.names: List[str] = []

    def __call__(self, tutorials: QuerySet = ()) -> Validator:
        for element in tutorials:
            self.names.append(element.name)
        return self

    def validate(self, document: Document) -> None:
        name = document.text.strip()
        if not self.regex.match(name):
            raise ValidationError(message='The name is not valid. '
                                          'It should only contain letters, numbers, dashes, and spaces.',
                                  cursor_position=len(name) - 1)
        if name in self.names:
            raise ValidationError(message='The name {} is taken. Please enter a new name!'.format(name),
                                  cursor_position=len(name) - 1)


class UrlValidator(Validator):
    regex = re.compile(r'^[a-zA-Z0-9-]+\Z')

    def __init__(self):
        super().__init__()
        self.urls: List[str] = []

    def __call__(self, tutorials: QuerySet) -> Validator:
        for element in tutorials:
            self.urls.append(element.url)
        return self

    def validate(self, document: Document) -> None:
        url = document.text.strip()
        if not self.regex.match(url):
            raise ValidationError(message='The url is not valid'
                                          'It should only contain letters, numbers and dashes.',
                                  cursor_position=len(url) - 1)
        if url in self.urls:
            raise ValidationError(message='The url {} is taken. Please enter a new url!'.format(url),
                                  cursor_position=len(url) - 1)


class LocationValidator(Validator):
    def validate(self, document: Document) -> None:
        if not pathlib.Path(document.text).exists():
            raise ValidationError(message='Please input a valid path!')


_path_completer = PathCompleter()
_tutorial_source_folder_validator = TutorialSourceFolderValidator()
_name_validator = NameValidator()
_url_validator = UrlValidator()
_location_validator = LocationValidator()


def new_line_prompt(*args, **kwargs) -> str:
    message = kwargs.pop('message', '\n') + '\n'
    return prompt(message=message, *args, **kwargs)


@new_session('input location')
def get_location(prompt_text: str = 'Please enter location',
                 validator: Validator = _location_validator) -> pathlib.Path:
    return pathlib.Path(new_line_prompt(message=prompt_text,
                                        validator=validator,
                                        completer=_path_completer, ))


@new_session('input name')
def get_name(message: str = '', validator: Validator = None, default: str = '') -> str:
    return new_line_prompt(message=message,
                           validator=validator,
                           default=default).strip()


@new_session('input url')
def get_url(message: str = '', validator: Validator = None, default: str = '') -> str:
    return new_line_prompt(message=message,
                           validator=validator,
                           default=default.replace(' ', '-')).strip()


@new_session('input abstract')
def get_abstract(message: str = '', validator: Validator = None, default: str = '', multiline=True) -> str:
    return new_line_prompt(message=message, validator=validator, default=default, multiline=multiline)


@new_session('select and add categories')
def select_and_add_categories() -> List[CategoryWrapper]:
    category_query_set: QuerySet = Category.objects.all()
    category_selections: List[Tuple[Category, str]] = [(model, model.category) for model in category_query_set]

    category_choices: List[Category] = run_interruptable_checkbox_dialog(
        text='Please choose existing categories: ',
        values=category_selections
    )

    new_categories: Iterable[str] = map(
        lambda x: x.strip(),
        new_line_prompt('Please enter new categories. Separate with ";"').split(';')
    )

    return [CategoryWrapper().load_model(category_model)
            for category_model in category_choices if category_model] + \
           [CategoryWrapper().set_variables(category_name=category_name)
            for category_name in new_categories if category_name]


@new_session('select authors')
def select_authors() -> List[UserWrapper]:
    user_query_set: QuerySet = User.objects.all()
    user_selections: List[Tuple[User, str]] = [(model, f'{model.username}: {model.email}') for model in user_query_set]

    user_choices: List[User] = run_interruptable_checkbox_dialog(
        text='Please choose authors: ',
        values=user_selections
    )

    return [UserWrapper().load_model(user_model) for user_model in user_choices if user_model]


@new_session('select graph priority')
def select_graph_priority() -> int:
    return int(inline_radio_dialog(text='Please select the priority of this graph',
                                   values=[(60, 'major graph',),
                                           (40, 'minor graph',),
                                           (20, 'trivial graph')]).run())


@new_session('select matching tutorials')
def select_tutorials() -> List[TutorialAnchorWrapper]:
    tutorial_query_set = Tutorial.objects.all()
    tutorial_selections = [(model, f'{model.url}: {model.name}') for model in tutorial_query_set]

    tutorial_choices: List[Tutorial] = run_interruptable_checkbox_dialog(
        text='Please select tutorials',
        values=tutorial_selections
    )

    return [TutorialAnchorWrapper().load_model(tutorial_model) for tutorial_model in tutorial_choices if tutorial_model]


@new_session('select matching tutorial')
def select_tutorial() -> TutorialAnchorWrapper:
    tutorial_query_set = Tutorial.objects.all()
    tutorial_selections = [(model, f'{model.url}: {model.name}') for model in tutorial_query_set]

    tutorial_choice: Tutorial = inline_radio_dialog(
        text='Please select a tutorial',
        values=tutorial_selections
    ).run()

    return TutorialAnchorWrapper().load_model(tutorial_choice)


@new_session('select language')
def select_lang(default_lang: str = 'en-us') -> Type[TranslationBase]:
    lang_selections = [(cls, f'{lang[:2]}-{lang[2:]}') for lang, cls in translation_table_mapping.items()]

    lang_choice: Type[TranslationBase] = inline_radio_dialog(text='Please select the language',
                                                             values=lang_selections,
                                                             default_value=(get_translation_table(default_lang),
                                                                            default_lang)).run()
    return lang_choice


def proceed_prompt(actions: Callable) -> None:
    proceed = prompt('Proceed? (y/N) ')
    if proceed.lower() == 'y':
        actions()
        commit()
        print_formatted_text('Changes committed.')
    else:
        print_formatted_text('Changes not saved. Rolling back.')
        rollback()
        print_formatted_text('Rolled back')


def gather_tutorial_anchor_info() -> TutorialAnchorWrapper:
    tutorial_query_set: QuerySet = Tutorial.objects.all()

    print_formatted_text('For naming convention, please visit https://poppy-poppy.github.io/Graphery/')

    name: str = get_name(message='Please enter the name of the tutorial: ',
                         validator=_name_validator(tutorial_query_set))

    url: str = get_url(message='Please enter the url of the tutorial: ',
                       validator=_url_validator(tutorial_query_set),
                       default=name)

    categories = select_and_add_categories()

    return TutorialAnchorWrapper().set_variables(url=url,
                                                 name=name,
                                                 categories=categories)


def create_tutorial_anchor() -> None:
    anchor_wrapper = gather_tutorial_anchor_info()
    print_formatted_text('Tutorial anchor created')
    print_formatted_text('name: {}'.format(anchor_wrapper.name))
    print_formatted_text('url: {}'.format(anchor_wrapper.url))
    print_formatted_text('categories: {}'.format(anchor_wrapper.categories))
    result = prompt('Proceed? (y/N) ')

    if result.lower() == 'Y':
        anchor_wrapper.prepare_model()
        anchor_wrapper.finalize_model()
        commit()
        print_formatted_text('Changes committed')
    else:
        print_formatted_text('Changes not saved. Rolling back.')
        rollback()
        print_formatted_text('Rolled back.')


@new_session('Graph Json Location')
def gather_graph_json() -> List[pathlib.Path]:
    graphs: List[pathlib.Path] = []

    graph_location = get_location('Please enter the folder location containing graph jsons: ')
    if graph_location.is_dir():
        graphs.extend(graph_location.glob('*.json'))
    elif graph_location.is_file() and graph_location.suffix == '.json':
        graphs.append(graph_location)

    if len(graphs) < 1:
        raise

    graph_selection_values = [(element, element.name) for element in graphs]

    selected_graph_file_paths = run_interruptable_checkbox_dialog(
        text='Please select the graphs you want to upload',
        values=graph_selection_values,
        default_values=graph_selection_values
    )

    return selected_graph_file_paths


def validate_graph_json(graph_file_path: pathlib.Path) -> Mapping:
    js_string = graph_file_path.read_text()

    try:
        js_obj = json.loads(js_string)
        if js_obj.get('elements', None) is None:
            raise InvalidGraphJson('The graph json (cyjs) must contain `element` object')
    except TypeError as e:
        raise InvalidGraphJson('The json input is not right: {}'.format(e))
    except json.JSONDecodeError:
        raise InvalidGraphJson("The json is malformatted. If you believe it's the program's fault, "
                               "please contact the developer")

    # TODO load the json into the custom graph object

    return js_obj


def gather_graph_info(graph_file_path: pathlib.Path) -> GraphWrapper:
    try:
        graph_json_obj: Mapping = validate_graph_json(graph_file_path)
    except InvalidGraphJson:
        raise

    name: str = get_name(message='Please input the name of the graph in {}'.format(graph_file_path.name),
                         validator=_name_validator,
                         default=graph_file_path.stem)

    url: str = get_url(message='Please input the url of the graph in {}'.format(graph_file_path.name),
                       validator=_url_validator,
                       default=name)

    matching_tutorials = select_tutorials()
    categories: List[CategoryWrapper] = select_and_add_categories()
    authors: List[UserWrapper] = select_authors()

    priority: int = select_graph_priority()

    return GraphWrapper().set_variables(
        url=url,
        name=name,
        categories=categories,
        authors=authors,
        priority=priority,
        cyjs=graph_json_obj,
        tutorials=matching_tutorials
    )


def wrap_graph_jsons(graph_paths: List[pathlib.Path]) -> List[GraphWrapper]:
    return [gather_graph_info(path) for path in graph_paths]


def create_graph() -> None:
    graph_file_paths = gather_graph_json()
    print_formatted_text('The graph json found: ')
    for path in graph_file_paths:
        print_formatted_text('  {}'.format(path.absolute()))

    graph_wrappers: List[GraphWrapper] = wrap_graph_jsons(graph_file_paths)

    print_formatted_text('The following graphs are created: ')
    if graph_wrappers:
        for wrapper in graph_wrappers:
            print_formatted_text(f'{wrapper}')
    else:
        print_formatted_text('None')
        print_formatted_text('No actions taken')
        return

    def actions():
        for graph_wrapper in graph_wrappers:
            graph_wrapper.prepare_model()
            graph_wrapper.finalize_model()

    proceed_prompt(actions=actions)


def get_locale_md_files() -> List[pathlib.Path]:
    source_folder: pathlib.Path = get_location(prompt_text='Please choose the tutorial translation folder')
    md_file_paths: List[pathlib.Path] = [path for path in source_folder.glob('*.md')]

    md_selection_values = [(element, element.name) for element in md_file_paths]

    selected_graph_file_paths = run_interruptable_checkbox_dialog(
        text='Please select the graphs you want to upload',
        values=md_selection_values,
        default_values=md_selection_values
    )
    return selected_graph_file_paths


def parse_markdown(text: str) -> Tuple[str, str]:
    result: str = markdown.markdown(text, extensions=['codehilite', 'md_in_html', 'markdown_del_ins',
                                                      'pymdownx.arithmatex', 'pymdownx.details',
                                                      'pymdownx.inlinehilite', 'pymdownx.superfences'])
    parser = CustomHtmlParser()
    parser.feed(result)
    abstract: str = ''.join(parser.data)

    return result, abstract
    # TODO add arithmatex required js to the page


def gather_locale_md_info(path: pathlib.Path) -> TutorialTranslationContentWrapper:
    try:
        name, lang = path.stem.split('.')
        # TODO I don't think you can do much about it since you can't change the input source in the command line?
        title: str = get_name(message='Please edit the title of this tutorial', default=name)
        lang_class: Type[TranslationBase] = select_lang(lang)

        content_md = path.read_text()
        content_html, abstract = parse_markdown(text=content_md)

        # TODO again, you can't do much in a command line I guess?
        abstract: str = get_abstract(message='Edit the abstract of this translation', default=abstract)

        authors = select_authors()
        tutorial_anchor = select_tutorial()

        return TutorialTranslationContentWrapper().set_variables(
            model_class=lang_class,
            title=title,
            authors=authors,
            tutorial_anchor=tutorial_anchor,
            abstract=abstract,
            content_md=content_md,
            content_html=content_html
        )

    except ValueError as e:
        e.args = ('Please follow the naming convention',)


def gather_md_files(md_file_paths: List[pathlib.Path]) -> List[TutorialTranslationContentWrapper]:
    return [gather_locale_md_info(path) for path in md_file_paths]


def create_locale_md() -> None:
    md_paths = get_locale_md_files()
    if not md_paths:
        print_formatted_text('Nothing is selected. Exiting')
        return
    md_file_wrappers = gather_md_files(md_paths)

    # TODO the incorporate edit mode. In the current frame work, this will just load the model from the database
    #  if it's already in there and does basically nothing to it. You should show a warning for now and
    #  and a edit option to it later. Same as for graphs.

    print_formatted_text('The following translations are created: ')
    for wrapper in md_file_wrappers:
        print_formatted_text(f'{wrapper}')

    def actions():
        for md_file_wrapper in md_file_wrappers:
            md_file_wrapper.prepare_model()
            md_file_wrapper.finalize_model()

    proceed_prompt(actions=actions)


def get_code_source_folder() -> pathlib.Path:
    return get_location(validator=_code_source_folder_validator)


def get_code_text_and_graph_req(source_folder_path: pathlib.Path) -> Tuple[str, Sequence[str]]:
    json_obj = json.loads((source_folder_path / 'graph-info.json').read_text())

    if 'required_graphs' in json_obj:
        return (source_folder_path / 'entry.py').read_text(), json_obj['required_graphs']
    raise


def code_executor(code_folder: pathlib.Path,
                           graph_object_mappings: Mapping[Graph, CustomGraph]) -> Mapping[Graph, Mapping]:
    exec_result = {}

    with controller as folder_creator, \
            folder_creator(f'temp_code_folder_{time.time()}') as cache_folder, \
            TempSysPathAdder(cache_folder):
        for any_file in code_folder.glob('*'):
            # noinspection PyTypeChecker
            shutil.copy(any_file, cache_folder / any_file.name)

        try:
            imported_module = import_module('entry')

            # TODO a better maybe?
            if not hasattr(imported_module, 'graph_object') or not hasattr(imported_module, 'main'):
                raise

            main_function = getattr(imported_module, 'main', None)

            for graph_name, graph_obj in graph_object_mappings.items():
                # I did not see this coming. I need to change the controller
                controller.purge_records()

                setattr(imported_module, 'graph_object', graph_obj)
                main_function()

                controller.generate_processed_record()

                exec_result[graph_name] = controller.get_processed_result()
        except ImportError:
            raise
        except Exception:
            raise

        return exec_result


def gather_code_info(code_folder: pathlib.Path) -> Tuple[CodeWrapper, Sequence[ExecResultJsonWrapper]]:
    code_text, required_graph_urls = get_code_text_and_graph_req(code_folder)
    if len(required_graph_urls) < 1:
        raise

    tutorial_anchor = select_tutorial()

    graph_id_obj_mapping: MutableMapping[Graph, CustomGraph] = {}

    # change this part. May not using url is a better idea
    for graph_url in required_graph_urls:
        graph_model_obj: Graph = Graph.objects.get(url=graph_url)
        graph_obj: CustomGraph = CustomGraph.graph_generator(graph_model_obj.cyjs)
        graph_id_obj_mapping[graph_model_obj] = graph_obj

    exec_result_mapping: Mapping[Graph, Mapping] = code_executor(code_folder, graph_id_obj_mapping)

    code_wrapper: CodeWrapper = CodeWrapper().set_variables(
        tutorial=tutorial_anchor,
        code=code_text
    )

    exec_result_wrappers = [ExecResultJsonWrapper().set_variables(
        code=code_wrapper,
        graph=GraphWrapper().load_model(graph_obj),
        json=exec_result_json_obj
    ) for graph_obj, exec_result_json_obj in exec_result_mapping.items()]

    return code_wrapper, exec_result_wrappers


def create_code_obj() -> None:
    code_source_folder = get_code_source_folder()
    code_wrapper, exec_result_wrappers = gather_code_info(code_source_folder)

    print_formatted_text('Code: {}'.format(code_wrapper))
    print_formatted_text('Execution results: ')
    for wrapper in exec_result_wrappers:
        print_formatted_text(f'{wrapper}')

    def actions():
        code_wrapper.prepare_model()
        code_wrapper.finalize_model()
        for result_wrapper in exec_result_wrappers:
            result_wrapper.prepare_model()
            result_wrapper.finalize_model()

    proceed_prompt(actions=actions)


def parse_entry_module() -> None:
    pass


def save_to_local_json() -> None:
    pass


class CommandWrapper:
    # use instance instead of class, so that I can have a recent create list.
    @staticmethod
    def create():
        create_tutorial_anchor()

    @staticmethod
    def add():
        print_formatted_text('Coming soon!')

    @staticmethod
    def modify():
        print_formatted_text('Coming soon!')

    @classmethod
    def run_command(cls, command: str) -> None:
        getattr(cls, command)()
