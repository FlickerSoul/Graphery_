<template>
  <div>
    <div>
      <q-card>
        <q-card-section>
          <UserInfoItem
            :title="$t('account.Username')"
            :content="username"
          ></UserInfoItem>
          <UserInfoItem
            :title="$t('account.Email')"
            :content="userEmail"
          ></UserInfoItem>
          <UserInfoItem
            :title="$t('account.Role')"
            :content="userRole"
          ></UserInfoItem>
          <UserInfoItem
            :title="$t('account.firstName')"
            :content="userFirstName"
          />
          <UserInfoItem
            :title="$t('account.lastName')"
            :content="userLastName"
          />
        </q-card-section>
        <q-separator />
        <q-card-actions align="center">
          <q-btn
            flat
            :label="$t('account.ControlPanel')"
            to="/control-panel"
            v-if="isAuthor || isTranslator || isAdmin"
          >
          </q-btn>
          <q-btn
            flat
            :label="$t('account.DjangoAdminPage')"
            v-if="isAdmin"
            type="a"
            :href="djangoAdminUrl"
            target="_blank"
          />
          <q-btn flat :label="$t('nav.Home')" :to="{ name: 'Home' }" />
          <q-btn flat :label="$t('account.LogOut')" @click="$emit('logout')" />
        </q-card-actions>
      </q-card>
    </div>
    <div id="edit-info" class="q-mt-xl">
      <EditUserInfoCard :user-obj="this.userObj" />
    </div>
  </div>
</template>

<script>
  import { BASE_URL } from '@/services/api_entry';
  import UserInfoItem from '@/components/user/UserInfoItem';
  import EditUserInfoCard from '@/components/user/EditPasswordCard';
  export default {
    props: ['userObj'],
    components: {
      UserInfoItem,
      EditUserInfoCard,
    },
    data() {
      return {
        djangoAdminUrl: BASE_URL + '/admin',
      };
    },
    computed: {
      username() {
        if (this.userObj) {
          return this.userObj['username'];
        }
        return 'Unavailable';
      },
      userEmail() {
        if (this.userObj) {
          return this.userObj['email'];
        }
        return 'Unavailable';
      },
      userRole() {
        if (this.userObj) {
          return this.userObj['role'];
        }
        return 'Unavailable';
      },
      userFirstName() {
        if (this.userObj) {
          return this.userObj['firstName'];
        }
        return 'Unavailable';
      },
      userLastName() {
        if (this.userObj) {
          return this.userObj['lastName'];
        }
        return 'Unavailable';
      },
      isAdmin() {
        return this.userRole === 'Administrator';
      },
      isAuthor() {
        return this.userRole === 'Author';
      },
      isTranslator() {
        return this.userRole === 'Translator';
      },
      isVisitor() {
        return this.userRole === 'Visitor';
      },
    },
  };
</script>
