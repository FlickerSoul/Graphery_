<template>
  <div>
    <MaterialCover :cover-title="$t('nav.About')" />
    <MaterialPage class="content-wrapper">
      <article class="about-content">
        <header>
          <h3 class="material-page-shorter-h3">
            {{ $t('nav.About') }}
          </h3>
          <img :src="logoSrc" class="logo" alt="" />
          <q-separator />
        </header>
        <section style="margin-top: 1rem">
          <p>
            Graphery is a web-based graph algorithm tutorial that is designed
            for biological researchers.
          </p>
          <!-- FIXME: The context is only English -->
          <p>
            It is organized around the concept of a tutorial, which describes
            and provides code for a classic graph algorithm. A tutorial contains
            three parts: text-based content, interactive graphs, and a code
            editor. The editor enables users to step forward and back in the
            code and see changes applied to the corresponding graph. The editor
            also allows more programming-savvy users to edit the existing code
            and see their modifications applied on the graphs. Users can run
            code in the editor locally or in the cloud. Together, these three
            panels allow users to gain a deeper understanding of the algorithm
            described.
          </p>
          <p>
            For each tutorial, users may select one of multiple real-world
            biological networks to better understand the implications of the
            algorithm described. These small graphs will come from from
            biological applications such as animal social networks, ecology food
            webs, molecular interaction networks, and phylogenetic trees.
          </p>
          <p>
            By accessing Graphery, you agree to the terms of service and privacy
            notice, which you can learn more from
            <router-link :to="{ name: 'TOS' }">here</router-link>.
          </p>
        </section>
        <section>
          <h4 id="feedback">
            Feedback
          </h4>
          <div>
            <p>
              Check
              <router-link :to="{ name: 'FAQ' }"
                >Frequently Asked Questions (FAQ)
              </router-link>
              first, or
            </p>
            <FeedbackDropdown />
          </div>
        </section>
        <section>
          <h4>Project Team</h4>
          <h5>Project Lead</h5>
          <p>
            <a href="https://www.reed.edu/biology/ritz/" target="_blank">
              Anna Ritz
            </a>
            is an Associate Professor of Biology at
            <a href="https://reed.edu" target="_blank"> Reed College</a>. A
            computer scientist by training, she does research in computational
            systems molecular biology. Dr. Ritz primarily develops graph
            algorithms to analyze signaling pathways in large protein-protein
            interaction networks.
          </p>
          <h5>
            Contributors
          </h5>
          <ul class="uo-list">
            <li>
              Heyuan Zeng, Computer Science Department, Reed College
            </li>
            <li>
              Jinbiao Zhang, Computer Science Department, Xiamen University
              Malaysia
            </li>
            <li>Gabriel Preising, Biology Department, Reed College</li>
            <li>
              Tobias Rubel, Biology and Philosophy Departments, Reed College
            </li>
            <li>Pramesh Singh, Biology Department, Reed College</li>
          </ul>
        </section>
        <section>
          <h4>
            Funding
          </h4>
          <p>
            This project is supported by an NSF CAREER Award (<a
              href="https://nsf.gov/awardsearch/showAward?AWD_ID=1750981"
              target="_blank"
              >DBI-1750981</a
            >) to Anna Ritz.
          </p>
        </section>
        <section>
          <h4>
            Libraries
          </h4>
          <p>
            This website can't be done without the following open source
            libraries. Big thanks to all the contributors directly and
            indirectly making this project happen.
          </p>
          <ul class="uo-list">
            <li>
              <NewTabA link="https://quasar.dev/"> Quasar </NewTabA>
            </li>
            <li>
              <NewTabA link="https://vuejs.org">Vue.JS</NewTabA>
            </li>
            <li>
              <NewTabA link="https://github.com/hinesboy/mavonEditor">
                Mavon Editor
              </NewTabA>
            </li>
            <li>
              <NewTabA link="https://github.com/markdown-it/markdown-it">
                Markdown It
              </NewTabA>
            </li>
            <li>
              <NewTabA
                link="https://github.com/markdown-it/markdown-it#syntax-extensions"
              >
                Markdown It Extensions
              </NewTabA>
            </li>
            <li>
              <NewTabA link="https://github.com/cytoscape/cytoscape.js">
                Cytoscape.JS
              </NewTabA>
            </li>
            <li>
              <NewTabA link="https://js.cytoscape.org/#extensions">
                Cytoscape.JS Extensions
              </NewTabA>
            </li>
            <li>
              <NewTabA link="https://github.com/atomiks/tippyjs">
                Tippy.JS
              </NewTabA>
            </li>
            <li>
              <NewTabA link="https://github.com/Microsoft/monaco-editor">
                Monaco Editor
              </NewTabA>
            </li>
            <li>
              <NewTabA link="https://github.com/cool-RR/PySnooper">
                PySnooper
              </NewTabA>
            </li>
            <li>
              <NewTabA link="https://www.djangoproject.com/"> Django </NewTabA>
            </li>
            <li>
              <NewTabA link="https://github.com/graphql-python/graphene-django">
                Graphene Django
              </NewTabA>
            </li>
            <li>
              <NewTabA link="https://www.postgresql.org/"> PostgreSQL </NewTabA>
            </li>
            <li>
              <NewTabA link="https://redis.io/">Redis</NewTabA>
            </li>
          </ul>
        </section>
        <section>
          <LicenseCard></LicenseCard>
        </section>
      </article>
    </MaterialPage>
  </div>
</template>

<script>
  import MaterialPage from '@/components/framework/MaterialPage.vue';
  import FeedbackDropdown from '@/components/framework/FeedbackDropdown';
  import MaterialCover from '@/components/framework/MaterialCover';

  export default {
    data() {
      return {
        logoSrc: require('@/assets/images/compbio-lab.png'),
      };
    },
    metaInfo() {
      const titleText = this.$t('nav.About');
      return { title: titleText };
    },
    components: {
      MaterialCover,
      MaterialPage,
      FeedbackDropdown,
      NewTabA: () => import('../components/framework/NewTabA'),
      LicenseCard: () => import('@/components/framework/LicenseCard.vue'),
    },
  };
</script>

<style lang="sass" scoped>
  .about-content
    p
      // 1rem = 16px ? to me
      font-size: 1rem
  .uo-list
    font-size: 1.1rem

  .content-wrapper
    //top: -8rem
    .logo
      float: right
      width: 160px
      height: 160px
      margin: 1rem
</style>
