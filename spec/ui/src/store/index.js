import { apiServerHost } from '@/utils.js';
import {createStore} from 'vuex'
import {notifyLoginFail} from '@/utils.js'
import createPersistedState from "vuex-persistedstate";

const initialState = {
  authenticated: localStorage.getItem('authenticated') || '',
  username: localStorage.getItem('username') || '',
  failedLogin: false,
  isAdmin: false,
};

const getters = {
  authenticated: state => {
    return state.authenticated === 'success'? true : false;
  },
  username: state => {
    return state.authenticated? state.username : null;
  },
  failedLogin: state => state.failedLogin,
  isAdmin: state => state.isAdmin,
};

const actions = {
  async checkAuthentication({ commit }) {
    let res = await window.fetch(`${apiServerHost}/api/auth_status/`, {
      credentials: 'include',
    });
    if (res.ok) {
      let result = await res.json();
      if (result.is_authenticated) {
        commit('login', {
            username: result.username,
            isAdmin: result.isAdmin //assuming isAdmin is returned from the server
        });
      } else {
        commit('logout');
      }
    } else {
      // handle error
    }
  },
  async login({ commit }, payload) {
    let res = await window.fetch(`${apiServerHost}/accounts/login/`, {
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
      // Attempt to log out on the server. We don't care about the result.
      await window.fetch(`${apiServerHost}/accounts/logout/`);

      // Regardless of server response, commit the logout.
      commit('logout');

      // And redirect to the external login service.
      window.location.href = process.env.VUE_APP_LOGOUT_URL;
  },
  async getPermission({commit}) {
    let isAdmin = false;
    let res = await window.fetch(`${apiServerHost}/auth/info`, {
      credentials: 'include',
    });
    if (res.ok) {
      res = await res.json();
      isAdmin = res['is_admin'];
    } else {
      isAdmin = false;
      commit('logout');
    }
    commit('setPermission', {
      isAdmin: isAdmin,
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
    state.isAdmin = false;
  },
  setPermission(state, payload) {
    state.isAdmin = payload.isAdmin;
  },
};

export default new createStore ({
  state: initialState,
  getters: getters,
  actions: actions,
  mutations: mutations,
  plugins: [createPersistedState()],
});