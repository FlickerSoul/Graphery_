<template>
  <CollectionPage
    :title="$t('nav.Tutorials')"
    ref="collection"
    :query="query"
    :variables="{ translation: $i18n.locale }"
    :mappingFunction="
      (data) => {
        const input = data.allTutorialInfo.filter((ele) => ele.content);
        return input.map((ele) => {
          return {
            url: `/tutorial/${$i18n.locale}/${ele.url}`,
            categories: ele.categories,
            isAnchorPublished: ele.isPublished,
            rank: ele.rank,
            title: ele.content.title,
            authors: ele.content.authors,
            modifiedTime: ele.content.modifiedTime,
            abstract: ele.content.abstract,
            isTransPublished: ele.content.isPublished,
          };
        });
      }
    "
    :moreButtonText="$t('collectionPage.ReadMore')"
    :notClickableWhenNoContent="true"
  ></CollectionPage>
</template>

<script>
  import { allTutorialAbstractInfoQuery } from '@/services/queries';
  import CollectionPage from '@/components/CollectionEntry/CollectionPage';

  export default {
    metaInfo() {
      const titleText = this.$t('nav.Tutorials');
      return { title: titleText };
    },
    components: {
      CollectionPage,
    },
    data() {
      return {
        query: allTutorialAbstractInfoQuery,
      };
    },
  };
</script>
