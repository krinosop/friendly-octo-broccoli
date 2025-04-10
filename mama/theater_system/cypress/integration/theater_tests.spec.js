describe('Театральная система', () => {
  beforeEach(() => {
    cy.visit('/')
  })

  it('Тест входа в систему', () => {
    // Переходим на страницу входа
    cy.contains('Войти').click()
    
    // Пробуем войти с неверными данными
    cy.get('input[name="username"]').type('wrong_user')
    cy.get('input[name="password"]').type('wrong_pass')
    cy.get('button[type="submit"]').click()
    
    // Проверяем сообщение об ошибке
    cy.contains('Пожалуйста, введите правильные имя пользователя и пароль')
    
    // Входим с правильными данными
    cy.get('input[name="username"]').clear().type('admin_test')
    cy.get('input[name="password"]').clear().type('admin12345')
    cy.get('button[type="submit"]').click()
    
    // Проверяем успешный вход
    cy.url().should('include', '/home/')
    cy.contains('Добро пожаловать')
  })

  it('Тест создания представления', () => {
    // Входим как администратор
    cy.visit('/login/')
    cy.get('input[name="username"]').type('admin_test')
    cy.get('input[name="password"]').type('admin12345')
    cy.get('button[type="submit"]').click()
    
    // Переходим к созданию представления
    cy.contains('Представления').click()
    cy.contains('Добавить представление').click()
    
    // Заполняем форму
    cy.get('select[name="play"]').select(1)
    cy.get('input[name="date"]').type('2025-04-15T19:00')
    cy.get('input[name="tickets_available"]').type('100')
    cy.get('input[name="ticket_price"]').type('1000')
    cy.get('select[name="status"]').select('scheduled')
    
    // Отправляем форму
    cy.get('button[type="submit"]').click()
    
    // Проверяем успешное создание
    cy.url().should('include', '/performances/')
    cy.contains('Представление успешно добавлено')
  })

  it('Тест удаления представления', () => {
    // Входим как администратор
    cy.visit('/login/')
    cy.get('input[name="username"]').type('admin_test')
    cy.get('input[name="password"]').type('admin12345')
    cy.get('button[type="submit"]').click()
    
    // Переходим к списку представлений
    cy.contains('Представления').click()
    
    // Находим первое представление и переходим к его удалению
    cy.get('.card').first().find('a').contains('Удалить').click()
    
    // Подтверждаем удаление
    cy.contains('Вы уверены, что хотите удалить это представление?')
    cy.get('button[type="submit"]').click()
    
    // Проверяем успешное удаление
    cy.url().should('include', '/performances/')
    cy.contains('Представление успешно удалено')
  })
}) 