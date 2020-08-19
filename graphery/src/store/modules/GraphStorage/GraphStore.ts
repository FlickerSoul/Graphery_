import { RootState } from '@/store/states/state';

import {
  GraphStoreType,
  GraphType,
  GraphTypeFromQueryData,
} from './GraphStoreState';
import { ActionTree, GetterTree, MutationTree } from 'vuex';

// TODO remove the pseudo content!
const state: GraphStoreType = {
  graphObjectList: null,
  currentGraphId: null,
  currentGraphJsonString: null,
  // use v-for to spread graphs and make :key bind to id (or serial code?)
};

const mutations: MutationTree<GraphStoreType> = {
  LOAD_GRAPH_OBJECT_LIST(state, value: GraphType[]) {
    state.graphObjectList = value;
  },
  LOAD_CURRENT_GRAPH_ID(state, value: string) {
    state.currentGraphId = value;
  },
  LOAD_CURRENT_GRAPH_JSON_STRING(state, value: string) {
    state.currentGraphJsonString = value;
  },

  // clear states
  CLEAR_GRAPHS(state) {
    state.graphObjectList = null;
  },
  CLEAR_CURRENT_GRAPH_ID(state) {
    state.currentGraphId = null;
  },
  CLEAR_CURRENT_GRAPH_JSON_STRING(state) {
    state.currentGraphJsonString = null;
  },
};

const actions: ActionTree<GraphStoreType, RootState> = {
  loadGraphListFromQueryData({ commit }, graphList: GraphTypeFromQueryData[]) {
    commit('LOAD_GRAPH_OBJECT_LIST', graphList);
  },
  loadGraphListFromMatched({ commit }, graphList: GraphType[]) {
    commit('LOAD_GRAPH_OBJECT_LIST', graphList);
  },
  loadCurrentGraphJsonString({ commit }, graphJsonString: string) {
    commit('LOAD_CURRENT_GRAPH_JSON_STRING', graphJsonString);
  },
  loadCurrentGraphId({ commit }, graphId: string) {
    commit('LOAD_CURRENT_GRAPH_ID', graphId);
  },
  CLEAR_ALL({ commit }) {
    commit('CLEAR_GRAPHS');
    commit('CLEAR_CURRENT_GRAPH_ID');
    commit('CLEAR_CURRENT_GRAPH_JSON_STRING');
  },
};

const getters: GetterTree<GraphStoreType, RootState> = {
  graphObjectListEmpty(state) {
    return state.graphObjectList === null;
  },
  getGraphObjectList(state) {
    return state.graphObjectList;
  },
  getGraphObjectById: (state) => (id: string) => {
    // TODO may return undefined
    return (
      state.graphObjectList && state.graphObjectList.find((g) => g.id === id)
    );
  },
  getGraphObjectByIndex: (state) => (index: number) => {
    return state.graphObjectList && state.graphObjectList[index];
  },
  autoGeneratedCurrentGraphObject(state, getter) {
    return getter.getGraphObjectById(state.currentGraphId) || null;
  },
  autoGeneratedCurrentGraphJsonObj(state, getter) {
    const currentGraphObject = getter.autoGeneratedCurrentGraphObject;
    if (currentGraphObject && currentGraphObject.cyjs) {
      // which should always happen since the graphs are chosen by ids which corresponds
      // defined graphs
      return JSON.parse(currentGraphObject.cyjs);
    }
    return null;
  },
  autoGeneratedCurrentGraphContent(state, getter) {
    const currentGraphObject = getter.autoGeneratedCurrentGraphObject;
    if (currentGraphObject && currentGraphObject.content) {
      return currentGraphObject.content;
    }
    return null;
  },
};

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters,
};
