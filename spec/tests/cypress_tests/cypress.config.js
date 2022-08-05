const { defineConfig } = require('cypress')

module.exports = defineConfig({
  env: {
    ADMIN_USER: 'spec-sup-test01',
    ADMIN_PASSWD: '',
  },
  watchForFileChanges: false,
  viewportWidth: 1300,
  viewportHeight: 800,
  e2e: {
    setupNodeEvents(on, config) {},
    specPattern: ['cypress/e2e/e2e.js',  'cypress/e2e/doc.js', 'cypress/e2e/data.js'],
    experimentalSessionAndOrigin: true,
    baseUrl: 'http://127.0.0.1:8000',
  },

})
