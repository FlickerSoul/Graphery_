import Vue from 'vue';

import './styles/quasar.sass';
import '@quasar/extras/mdi-v5/mdi-v5.css';
import '@quasar/extras/material-icons/material-icons.css';
import {
  Quasar,
  QLayout,
  QHeader,
  QDrawer,
  QPageContainer,
  QPage,
  QToolbar,
  QToolbarTitle,
  QBtn,
  QIcon,
  QList,
  QItem,
  QItemSection,
  QItemLabel,
  // My extensions
  QBar,
  // QBreadcrumbs,
  // QBreadcrumbsEl,
  QIntersection,
  QCard,
  QCardSection,
  QCardActions,
  QChip,
  QInput,
  QFooter,
  QTooltip,
  QBtnDropdown,
  QBtnGroup,
  QDialog,
  QSlideTransition,
  QSeparator,
  QSelect,
  QInnerLoading,
  QSpinnerPie,
  // QTabs,
  // QTab,
  // QTabPanels,
  // QTabPanel,
  QPageSticky,
  QCircularProgress,
  QImg,
  QAvatar,
  QPagination,
  QResizeObserver,
  QSplitter,
  QSpace,
  QSlider,
  QToggle,
  QExpansionItem,
  QVirtualScroll,
  QFab,
  QFabAction,
  // My plugins
  Notify,
  // My directive
  TouchPan,
} from 'quasar';

Vue.use(Quasar, {
  config: {},
  components: {
    QLayout,
    QHeader,
    QDrawer,
    QPageContainer,
    QPage,
    QToolbar,
    QToolbarTitle,
    QBtn,
    QIcon,
    QList,
    QItem,
    QItemSection,
    QItemLabel,
    // my addons
    QBar,
    // QBreadcrumbs,
    // QBreadcrumbsEl,
    QIntersection,
    QCard,
    QCardSection,
    QCardActions,
    QChip,
    QInput,
    QFooter,
    QTooltip,
    QBtnDropdown,
    QBtnGroup,
    QDialog,
    QSlideTransition,
    QSeparator,
    QSelect,
    QInnerLoading,
    QSpinnerPie,
    // QTabs,
    // QTab,
    // QTabPanels,
    // QTabPanel,
    QPageSticky,
    QCircularProgress,
    QImg,
    QAvatar,
    QPagination,
    QResizeObserver,
    QSplitter,
    QSpace,
    QSlider,
    QToggle,
    QExpansionItem,
    QVirtualScroll,
    QFab,
    QFabAction,
  },
  directives: { TouchPan },
  plugins: { Notify },
});
