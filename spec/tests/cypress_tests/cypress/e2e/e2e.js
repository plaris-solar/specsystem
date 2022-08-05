describe('test Document Pages', () =>{
    

    beforeEach(() => {
      cy.login()
      const resizeObserverLoopErrRe = /^[^(ResizeObserver loop limit exceeded)]/
      Cypress.on('uncaught:exception', (err) => {
      /* returning false here prevents Cypress from failing the test */
      if (resizeObserverLoopErrRe.test(err.message)) {
            return false
        }
      })
    })

    it('Create New Page', () => {
      cy.visit(Cypress.config().baseUrl + '/ui-docs');
      cy.get_cy('doc-new-page-btn').click()
      cy.get_cy('doc-detail-doc-name').clear().type('test_page')
      cy.get_cy('doc-detail-id-col').prev().should('have.text', 'lot_id')
      cy.get_cy('doc-detail-doc-descr').clear().type('Test page for integration testing')

      // fill the five empty rows in the new doc page 
      for (let i=0; i<5; i++){
        cy.get_cy('doc-detail-col-').eq(0).scrollIntoView()
        cy.get_cy('doc-detail-col-').eq(0).clear().type(`test_col_${i}`)

      }

      // Change the datatype of the test_col_3 to number + set to required
      cy.get_cy('doc-detail-type-test_col_3').click()
      cy.click_in_listbox('number')
      cy.get_cy('doc-detail-req-test_col_3').click()

      // Add new row and fill with new_id_col
      cy.get_cy('doc-detail-row-btn').click()
      cy.get_cy('doc-detail-col-').clear().type(`new_id_col`)

      // Set the ID column to new_id_col and verify that it becomes a required column
      cy.get_cy('doc-detail-id-col').click()
      cy.click_in_listbox('new_id_col')
      cy.get_cy('doc-detail-req-new_id_col').children().should('have.class', 'q-checkbox__inner--truthy')

      cy.get_cy('doc-detail-save-btn').click()

      cy.notif_contains('Page updated successfully.')
    })

    it('Verify doc detail', () => {
      cy.visit(Cypress.config().baseUrl + '/ui-docs');
      cy.get_cy('doc-table').within(() => {
        cy.contains('td', 'TEST_PAGE').next().should('have.text', 'Test page for integration testing')
        cy.contains('td', 'TEST_PAGE').next().next().within(() => {
            for (const col of ['lot_id*', 'test_col_0', 'test_col_1', 'test_col_2', 'test_col_3*', 'test_col_4', 'new_id_col*']){
              cy.contains('div', col).should('exist')
            }
        })
      })
    })

    it('Upload test data csv', () => {
      const file = 'e2e_test_data.csv'

      cy.visit(Cypress.config().baseUrl + '/ui-docs');
      cy.get_cy('doc-table').contains('td', 'TEST_PAGE').click()

      cy.get_cy('app-upload-btn').click()
      cy.get_cy('app-upload-window').should('be.visible')

      cy.get_cy('app-upload-window').within(() => {
        cy.get_cy('upload-file-btn').attachFile(file)
        cy.get_cy('upload-upload-btn').click()
      })

      // verify success message and some data in table
      cy.check_notif_success()
      cy.get_cy('lot_id-111111').should('have.length', 20)

    })

})