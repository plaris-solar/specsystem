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
        cy.visit(Cypress.config().baseUrl + '/ui-docs');
    })

    it('Test delete doc row', () => {
        // Search for test_page in the listbox
        cy.get_cy('doc-table-select').click()
        cy.click_in_listbox('IQC_ROLLS')

        // Confirm that TEST_PAGE appears in the first cell (+1 offest for virtual scroll)
        cy.get_cy('doc-table').find('td').eq(1).should('have.text', 'IQC_ROLLS')
        cy.get_cy('doc-table').contains('td', 'IQC_ROLLS').click()
        
        // Delete LABELS row and save tables
        cy.get_cy('doc-detail-delete-LABELS').click()
        cy.get_cy('doc_detail-table').contains('td', 'LABELS').should('not.exist')

        cy.get_cy('doc-detail-row-btn').click()

        cy.get_cy('doc-detail-save-btn').click()
        cy.check_notif_success()
    })

    it('Test add doc row', () => {
        cy.contains('td', 'IQC_ROLLS').click()

        cy.get_cy('doc-detail-row-btn').click()
        cy.get_cy('doc-detail-col-').eq(0).clear().type('new_row')
        cy.get_cy('doc-detail-req-new_row').click()

        cy.get_cy('doc-detail-save-btn').click()
        cy.notif_contains('Unable to apply required column for document')

        cy.get_cy('doc-detail-req-new_row').click()
        cy.get_cy('doc-detail-save-btn').click()
        cy.check_notif_success()
    })

    it('Verify doc_type changes', () => {
        cy.contains('td', 'IQC_ROLLS').next().next().within(() => {
            for (const col of ['lot_id*', 'REV*', 'SUPPLIER_LOT', 'DOM', 'POV', 'SUPPLIER*', 'new_row']){
              cy.contains('div', col).should('exist')
            }
        })

        cy.get_cy('app-doc-select').click()
        cy.click_in_listbox('IQC_ROLLS')

        cy.wait(500)
        cy.get_cy('data-table').contains('th', 'LABELS').should('not.exist')

        cy.get_cy('data-table').within(() => {
            for (const col of ['lot_id', 'REV', 'SUPPLIER_LOT', 'DOM', 'POV', 'SUPPLIER', 'new_row']){
              cy.contains('th', col).should('exist')
            }
        })
    })

    it('Create new page from template', () => {
        cy.get_cy('doc-new-page-btn').click()
        cy.get_cy('doc-detail-doc-name').clear().type('template_test_page')
        cy.get_cy('doc-detail-id-col').prev().should('have.text', 'lot_id')
        cy.get_cy('doc-detail-doc-descr').clear().type('Test page for integration testing using template')
        cy.get_cy('doc-detail-csv-btn').attachFile('template_data.csv')
        cy.get_cy('doc_detail-table').within(() => {
            for (const col of ['lot_id', 'col1', 'col2', 'col3']){
                cy.get_cy(`doc-detail-col-${col}`).should('exist')
            }
            cy.get_cy('doc-detail-req-lot_id').children().should('have.class', 'q-checkbox__inner--truthy')
        })
        cy.get_cy('doc-detail-save-btn').click()
        cy.check_notif_success()

        cy.go('back')
        cy.go('back')
        cy.contains('td', 'TEMPLATE_TEST_PAGE').next().next().within(() => {
            for (const col of ['lot_id*', 'col1', 'col2', 'col3']){
              cy.contains('div', col).should('exist')
            }
        })
    })

    it('Create new page from existing', () => {
        cy.get_cy('doc-table').contains('td', 'TEMPLATE_TEST_PAGE').click()
        cy.get_cy('doc-detail-doc-name').clear().type('TEMPLATE_dup')
        cy.get_cy('doc-detail-doc-descr').clear().type('Duplicate test data collection')
        cy.get_cy('doc-detail-save-btn').click()
        cy.check_notif_success()
        cy.go('back')
        cy.go('back')

        cy.get_cy('doc-table-select').click()
        cy.click_in_listbox('TEMPLATE_DUP')
        cy.contains('td', 'TEMPLATE_DUP').next().next().within(() => {
            for (const col of ['lot_id*', 'col1', 'col2', 'col3']){
              cy.contains('div', col).should('exist')
            }
        })
    })


})