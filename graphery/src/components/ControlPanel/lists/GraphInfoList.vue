<template>
  <ControlPanelContentFrame>
    <template v-slot:title>
      Graph Info
    </template>
    <q-table
      :data="tableContent"
      :columns="columns"
      :pagination="pagination"
      :loading="loadingContent"
      no-data-label="No graph info is found."
      row-key="id"
      separator="cell"
      class="custom-table"
    >
      <template v-slot:top>
        <RefreshButton :fetch-func="fetchGraphInfo" class="q-mr-sm" />
        <LangSelector
          :current-lang="tableLang"
          :change-callback="changeTableLang"
          :show-header="true"
        />
      </template>
      <template v-slot:header="props">
        <AllTableHeader :passed-props="props" />
      </template>
      <template v-slot:body="props">
        <q-tr :props="props">
          <q-td key="title" :props="props">
            <OpenInEditorButton
              :label="props.row.title"
              :routePath="{
                name: 'Graph Info Editor',
                params: {
                  anchorId: props.row.graphId,
                  contentId: props.row.id,
                },
                query: {
                  lang: tableLang,
                  graphUrl: props.row.graphUrl,
                },
              }"
            />
          </q-td>

          <q-td key="isPublished" :props="props">
            {{ props.row.isPublished ? '✅' : '❌' }}
          </q-td>

          <q-td key="abstract" :props="props">
            <q-input v-model="props.row.abstract" type="textarea" readonly />
          </q-td>

          <q-td key="graphName" :props="props">
            {{ props.row.graphName }}
          </q-td>

          <q-td key="graphUrl" :props="props">
            <OpenInPageButton
              :label="props.row.graphUrl"
              :routePath="{
                name: 'Graph',
                params: { lang: tableLang, url: props.row.graphUrl },
              }"
            />
          </q-td>

          <q-td key="id" :props="props">
            {{ props.row.id }}
          </q-td>

          <DeleteTableCell
            :message="
              `Do you want to delete graph translation '${props.row.title} that belongs to graph '${props.row.graphName}' with id '${props.row.id}'?`
            "
            :id="props.row.id"
            :content-type="currentDeletionContentType"
            :final-callback="fetchGraphInfo"
          />
        </q-tr>
      </template>
    </q-table>
  </ControlPanelContentFrame>
</template>

<script>
  import loadingMixin from '../mixins/LoadingMixin.vue';
  import tableLangMixin from '../mixins/TableLangMixin.vue';
  import { apiCaller } from '@/services/apis';
  import { graphInfoListQuery } from '@/services/queries';
  import { errorDialog, resolveAndOpenLink } from '@/services/helpers';
  import { newModelUUID } from '@/services/params';
  import AllTableHeader from '@/components/ControlPanel/parts/table/AllTableHeader';

  export default {
    mixins: [loadingMixin, tableLangMixin],
    components: {
      DeleteTableCell: () =>
        import('@/components/ControlPanel/parts/table/DeleteTableCell'),
      AllTableHeader,
      OpenInPageButton: () => import('../parts/buttons/OpenInPageButton'),
      OpenInEditorButton: () => import('../parts/buttons/OpenInEditorButton'),
      ControlPanelContentFrame: () =>
        import('../frames/ControlPanelContentFrame.vue'),
      RefreshButton: () => import('../parts/buttons/RefreshButton.vue'),
      LangSelector: () => import('../parts/selectors/LangSelector.vue'),
    },
    data() {
      return {
        columns: [
          {
            name: 'title',
            label: 'title',
            field: 'title',
            align: 'center',
            sortable: true,
            sort: (a, b) => {
              if (a === b) {
                return 0;
              }

              return a < b ? -1 : 1;
            },
          },
          {
            name: 'isPublished',
            label: 'Published?',
            field: 'isPublished',
            align: 'center',
          },
          {
            name: 'abstract',
            label: 'Abstract',
            field: 'abstract',
            align: 'center',
          },
          {
            name: 'graphName',
            label: 'Graph Name',
            field: 'graphName',
            align: 'center',
          },
          {
            name: 'graphUrl',
            label: 'Graph URL',
            field: 'graphUrl',
            align: 'center',
          },
          {
            name: 'id',
            label: 'ID',
            field: 'id',
            align: 'center',
            required: true,
          },
        ],
        tableContent: [],
        pagination: {
          sortBy: 'title',
          rowsPerPage: 10,
        },
        graphContentTypeMapping: {
          'en-us': 'ENUS_GRAPH_CONTENT',
          'zh-cn': 'ZHCN_GRAPH_CONTENT',
          es: 'ES_GRAPH_CONTENT',
        },
      };
    },
    computed: {
      requestVariable() {
        return {
          translation: this.tableLang,
        };
      },
      currentDeletionContentType() {
        const contentType = this.graphContentTypeMapping[this.tableLang];
        if (contentType) {
          return contentType;
        } else {
          errorDialog({
            message: 'Internal Error: Unknown deletion content type specified.',
          });
          return undefined;
        }
      },
    },
    methods: {
      fetchGraphInfo() {
        this.startLoading();
        apiCaller(graphInfoListQuery, this.requestVariable)
          .then((data) => {
            if (!data || !('allGraphInfo' in data)) {
              throw Error('Invalid data returned.');
            }

            this.tableContent = data['allGraphInfo'].map((obj) => {
              obj.content.graphId = obj.id;
              obj.content.graphName = obj.name;
              obj.content.graphUrl = obj.url;
              return obj.content;
            });
          })
          .catch((err) => {
            errorDialog({
              message: `An error occurs during fetching graph info. ${err}`,
            });
          })
          .finally(() => {
            this.finishedLoading();
          });
      },
      createGraphInfo() {
        resolveAndOpenLink({
          name: 'Graph Info Editor',
          params: {
            id: newModelUUID,
          },
        });
      },
    },
    mounted() {
      this.fetchGraphInfo();
    },
    watch: {
      tableLang: function() {
        this.fetchGraphInfo();
      },
    },
  };
</script>
