Cypress.Commands.add('notif_contains', (txt) => {
    cy.get('[class="q-notification__message col"]').should('contain.text', txt).and('be.visible')
    cy.wait(500)
});

Cypress.Commands.add('check_notif_success', () => {
    cy.get('[class="q-notification__message col"]').should('contain.text', 'success').and('be.visible')
    cy.wait(500)
});

Cypress.Commands.add('type_in_cell', (cy_id, txt) => {
    if (txt !== ''){
        cy.get_cy(cy_id).first().clear().type(txt)
    }
    else{
        cy.get_cy(cy_id).first().clear()
    }
})

Cypress.Commands.add('visit_data_page', (page) => {
    cy.get_cy('app-doc-select').click()
    cy.click_in_listbox(page)
})

Cypress.Commands.add('filter_lot_id', (lot_id) => {
    cy.wait(500)
    cy.get_cy('data-filter-select').click().clear().type('lot_id')
    cy.click_in_listbox('lot_id')
    cy.get_cy('data-filter-input').clear().type(`${lot_id}{enter}`)
})

Cypress.Commands.add('check_notif_err', () => {
    cy.get('[class="q-notification__message col"]').should('contain.text', 'error').and('be.visible')
    cy.wait(500)
});

Cypress.Commands.add('get_cy', (cy_id) => {
    return cy.get(`[data-cy="${cy_id}"]`)
})

Cypress.Commands.add('login', () => {
    var username = Cypress.env('ADMIN_USER')
    var passwd = Cypress.env('ADMIN_PASSWD')
    cy.session([username, passwd], () => {
        cy.visit(Cypress.config().baseUrl);
        cy.get_cy('login-username-input').clear().type(username)
        cy.get_cy('login-password-input').clear().type(passwd)
        cy.contains('button', 'login').click()
        cy.wait(1000)
        cy.contains('Welcome').should('be.visible')
    })
})


Cypress.Commands.add('click_in_listbox', (list_item) => {
    cy.get('[class="q-menu q-position-engine scroll"]').contains(list_item).click()
})

Cypress.Commands.add('check_app_header', (header_txt) => {
    cy.get_cy('app-title').should('contain.text', header_txt)
})

Cypress.Commands.add('create_new_page', (template_file, page_name) => {
    cy.visit(Cypress.config().baseUrl + '/ui-docs');
    cy.get_cy('doc-new-page-btn').click()
    cy.get_cy('doc-detail-doc-name').clear().type(page_name)
    cy.get_cy('doc-detail-id-col').prev().should('have.text', 'lot_id')
    cy.get_cy('doc-detail-doc-descr').clear().type('Test page for integration testing using template')
    cy.get_cy('doc-detail-csv-btn').attachFile(template_file)
    cy.get_cy('doc-detail-save-btn').click()
    cy.check_notif_success()
})

Cypress.Commands.add('upload_data_csv', (page_name, data_csv) => {
    cy.get_cy('app-upload-btn').click()
    cy.get_cy('upload-doc-select').click()
    cy.click_in_listbox(page_name)
    cy.get_cy('upload-file-btn').attachFile(data_csv)
    cy.get_cy('upload-upload-btn').click()
    cy.check_notif_success()
})