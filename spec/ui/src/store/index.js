import { serverHost } from '@/utils.js';
import {createStore} from 'vuex'
import {notifyLoginFail} from '@/utils.js'
import createPersistedState from "vuex-persistedstate";

const initialState = {
  authenticated: localStorage.getItem('authenticated') || '',
  username: localStorage.getItem('username') || '',
  failedLogin: false,
  isSupervisor: false,
};

const getters = {
  authenticated: state => {
    return state.authenticated === 'success'? true : false;
  },
  username: state => {
    return state.authenticated? state.username : null;
  },
  failedLogin: state => state.failedLogin,
  isSupervisor: state => state.isSupervisor,
};

const actions = {
  async login({ commit }, payload) {
    let res = await window.fetch(`${serverHost}/accounts/login/`, {
      method: 'POST',
      credentials: 'include',
      body: payload.form,
    });
    var url = new URL(res.url);
    if (res.ok && (url.pathname !== '/accounts/login/')) { // If fail, it return the same URL.
      commit('login',
        {
          username: payload.form.get('username'),
        }
      );
    } else {
      commit('login_fail');
    }
  },
  async logout({ commit }) {
    let res = await window.fetch(`${serverHost}/accounts/logout/`);
    if (res.ok) {
      commit('logout');
    }
  },
  async getPermission({commit}) {
    let isSupervisor = false;
    let res = await window.fetch(`${serverHost}/auth/info`, {
      credentials: 'include',
    });
    if (res.ok) {
      res = await res.json();
      isSupervisor = res['is_supervisor'];
    } else {
      isSupervisor = false;
      commit('logout');
    }
    commit('setPermission', {
      isSupervisor: isSupervisor,
    });
  },
};

const mutations = {
  login(state, payload) {
    state.authenticated = 'success';
    state.username = payload.username;
    state.failedLogin = false;
    localStorage.setItem('authenticated', state.authenticated);
    localStorage.setItem('username', state.username);
  },
  login_fail() {
    notifyLoginFail('The username is unauthorized, or the password is incorrect. Note that both fields may be case-sensitive.');

  },
  logout(state) {
    state.authenticated = false;
    state.username = null;
    localStorage.setItem('authenticated', '');
    localStorage.setItem('username', '');
    state.isSupervisor = false;
  },
  setPermission(state, payload) {
    state.isSupervisor = payload.isSupervisor;
  },
};

export default new createStore ({
  state: initialState,
  getters: getters,
  actions: actions,
  mutations: mutations,
  plugins: [createPersistedState()],
});