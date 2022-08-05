describe('test Data Page', () =>{
    beforeEach(() => {
        cy.login()
        const resizeObserverLoopErrRe = /^[^(ResizeObserver loop limit exceeded)]/
        Cypress.on('uncaught:exception', (err) => {
        /* returning false here prevents Cypress from failing the test */
        if (resizeObserverLoopErrRe.test(err.message)) {
              return false
          }
        })
        cy.visit(Cypress.config().baseUrl);
    })
    
    it('Create new page from template', () => {
        cy.visit(Cypress.config().baseUrl + '/ui-docs');
        cy.get_cy('doc-new-page-btn').click()
        cy.get_cy('doc-detail-doc-name').clear().type('data_test_doc')
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
        cy.wait(500)
        cy.contains('td', 'DATA_TEST_DOC').next().next().within(() => {
            for (const col of ['lot_id*', 'col1', 'col2', 'col3']){
              cy.contains('div', col).should('exist')
            }
        })
    })

    it('Upload data csv', () => {
        cy.get_cy('app-upload-btn').click()

        cy.get_cy('upload-doc-select').click()
        cy.click_in_listbox('DATA_TEST_DOC')
        cy.get_cy('upload-file-btn').attachFile('data_test_data.csv')
        cy.get_cy('upload-upload-btn').click()
        cy.check_notif_success()
    })

    it('Add data via UI', () => {
        cy.get_cy('DATA_TEST_DOC').click()
        cy.wait(500)

        // Create three empty rows, save two rows of data
        cy.get_cy('data-row-btn').click().click().click()
        cy.type_in_cell('lot_id-null', 'lot1')
        cy.type_in_cell('col1-null', 'col1_val1')
        cy.type_in_cell('col2-null', 'col2_val1')
        cy.type_in_cell('col3-null', 'col3_val1')

        cy.type_in_cell('lot_id-null', 'lot2')
        cy.type_in_cell('col1-null', 'col1_val2')
        cy.type_in_cell('col3-null', 'col3_val2')

        cy.get_cy('data-save-btn').click()
        cy.notif_contains('Added 2 rows successfully.')
        
    })

    it('Test update data', () => {
        cy.visit_data_page('DATA_TEST_DOC')
        cy.get('td').should('have.length.greaterThan', 50)

        // Change col data of lot1
        cy.type_in_cell('col1-col1_val1', 'new_col1_val1')
        cy.type_in_cell('col2-col2_val1', 'new_col2_val1')
        cy.get('td').eq(1).click()

        cy.get('td').eq(1).children().children().should('have.class', 'q-checkbox__inner--truthy')

        // clear all data for lot_20
        cy.filter_lot_id('lot_20')
        cy.type_in_cell('col1-d20', '')
        cy.type_in_cell('col2-1', '')
        cy.type_in_cell('col3-FALSE', '')
        cy.get('td').eq(1).click()

        // change lot_id of lot_50 to lot_51
        cy.filter_lot_id('lot_50')
        cy.type_in_cell('lot_id-lot_50', 'lot_51')
        cy.get('td').eq(1).click()

        // clear filters and verify lot1 is still selected
        cy.get_cy('data-clear-filter-btn').click()
        cy.get('td').eq(1).children().children().should('have.class', 'q-checkbox__inner--truthy')
        cy.get_cy('data-save-btn').click()
        cy.notif_contains('Updated 3 rows successfully.')
    })

    it('Verify update test', () => {
        cy.visit_data_page('DATA_TEST_DOC')
        
        cy.filter_lot_id('lot1')
        cy.get_cy('col1-new_col1_val1').should('exist')
        cy.get_cy('col2-new_col2_val1').should('exist')
        cy.get_cy('col3-col3_val1').should('exist')

        // Verify lot_20 fields are deleted
        cy.filter_lot_id('lot_20')
        cy.get_cy('col1-null').should('exist')
        cy.get_cy('col2-null').should('exist')
        cy.get_cy('col3-null').should('exist')

        // Verify lot_50 was deleted/changed to lot_51
        cy.filter_lot_id('lot_50')
        cy.get_cy('lot_id-lot_50').should('not.exist')

        cy.filter_lot_id('lot_51')
        cy.get_cy('lot_id-lot_51').should('have.length', 2)
        cy.get_cy('col1-d50').should('exist')
        cy.get_cy('col2-1').should('exist')
        cy.get_cy('col3-FALSE').should('exist')

    })

    it("Test delete data", () => {
        cy.visit_data_page('DATA_TEST_DOC')

        cy.filter_lot_id('lot2')
        cy.wait(500)
        cy.get('td').eq(1).click()
        cy.get('td').eq(1).children().children().should('have.class', 'q-checkbox__inner--truthy')

        cy.filter_lot_id('lot_51')
        cy.wait(500)
        cy.get('td').eq(1).click()
        cy.get('td').eq(1).children().children().should('have.class', 'q-checkbox__inner--truthy')

        cy.filter_lot_id('lot_33')
        cy.wait(500)
        cy.get('td').eq(1).click()
        cy.get('td').eq(1).children().children().should('have.class', 'q-checkbox__inner--truthy')

        cy.get_cy('data-delete-btn').click()
        cy.notif_contains('Deleted 3 rows successfully.')
    })

    it("Verify test delete data", () => {
        cy.visit_data_page('DATA_TEST_DOC')

        cy.filter_lot_id('lot2')
        cy.get_cy('lot_id-lot2').should('not.exist')

        cy.filter_lot_id('lot_51')
        cy.get_cy('col1-d50').should('not.exist')

        cy.filter_lot_id('lot_33')
        cy.get_cy('lot_id-lot_33').should('not.exist')
    })

    it('Test data filter', () => {
        cy.create_new_page('data_filter_test_data', 'FILTER_TEST_DATA')
        cy.upload_data_csv('FILTER_TEST_DATA', 'data_filter_test_data.csv')
        cy.get_cy('data-num-pages').should('contain.text', 10)

        cy.get_cy('data-advanced-filter-btn').click()

        cy.get_cy('filter-select-0').click()
        cy.click_in_listbox('lot_id')
        cy.get_cy('filter-input-0').clear().type('lot_1')
        cy.get_cy('filter-apply-btn').click()

        cy.wait(500)

        cy.get_cy('lot_id-lot_1').should('have.length', 2)
        cy.get_cy('data-num-pages').should('contain.text', 1)

        cy.get_cy('data-advanced-filter-btn').click()
        cy.get_cy('filter-select-1').click()
        cy.click_in_listbox('col3')
        cy.get_cy('filter-input-1').clear().type('red')
        cy.get_cy('filter-apply-btn').click()

        cy.get_cy('lot_id-lot_1').should('have.length', 1)
        cy.get_cy('lot_id-lot_2').should('not.exist')

        cy.get_cy('data-advanced-filter-btn').click()
        cy.get_cy('filter-select-2').click()
        cy.click_in_listbox('col2')
        cy.get_cy('filter-input-2').clear().type('green')
        cy.get_cy('filter-apply-btn').click()

        cy.get_cy('lot_id-lot_1').should('not.exist')

        cy.get_cy('data-clear-filter-btn').click()
        cy.get_cy('data-num-pages').should('contain.text', 10)
    })


})