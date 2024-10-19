@router.message(F.text == "/start")
async def start_command(message: types.Message, state: FSMContext):
    userID = message.from_user.id
    
    # Extract arguments manually from the /start command
    args = message.text.split(" ", 1)
    company_id = None
    group_id = None
    
    # If there are any arguments, try to parse them
    if len(args) > 1:
        params = dict(param.split('=') for param in args[1].split('&'))
        company_id = params.get('start')
        group_id = params.get('group')

    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT role, company_id FROM user WHERE userID = ?", (userID,))
        user = cursor.fetchone()
        userToken = await generate_user_token()
        
        if user:
            # If the user already exists in the database
            role, existing_company_id = user
            
            if existing_company_id and existing_company_id != company_id:
                # User is already registered and linked to a different company
                await message.answer("Вы уже зарегистрированы и присоединены к компании. Вы не можете присоединиться к другой компании.")
                await main_menu(message, state, role=role)
                return
            
            # If the user is already registered and in the same company (or no referral)
            complete = await ask_for_next_missing_field(message, state)
            if complete:
                if role == 'Boss' and not existing_company_id:
                    # If user is a 'Boss' and has no company assigned
                    await ask_for_company(message, state)
                else:
                    await message.answer("Вы уже зарегистрированы и присоединены к компании. Добро пожаловать!")
                    await main_menu(message, state, role=role)
        else:
            # If the user is not in the database, proceed with registration
            if company_id:
                # Assign the role "Worker" when joining through a referral link
                cursor.execute("INSERT INTO user (userID, userToken, role, company_id) VALUES (?, ?, ?, ?)", 
                               (userID, userToken, "Worker", company_id))
                if group_id:
                    # Associate the user with the specific group if provided
                    cursor.execute("INSERT OR IGNORE INTO user_group_assignment (user_id, group_id) VALUES (?, ?)", 
                                   (userID, group_id))
                conn.commit()
                
                await message.reply("Добро пожаловать! Вы зарегистрированы как сотрудник компании через реферальную ссылку.")
            else:
                # If the user didn't join via a referral link, assign the role "Boss"
                cursor.execute("INSERT INTO user (userID, userToken, role) VALUES (?, ?, ?)", (userID, userToken, "Boss"))
                conn.commit()
                await message.reply("Добро пожаловать! Пожалуйста, давайте приступим к процессу регистрации как руководитель компании.")
                
            # Start the registration process for the user
            await ask_for_next_missing_field(message, state)

@router.callback_query(lambda call: call.data.startswith("list_of_employees"))
async def show_list_of_employees(callback_query: types.CallbackQuery, state: FSMContext):
    # Check if the callback data contains a page number
    if "page" in callback_query.data:
        page = int(callback_query.data.split("_")[-1])
    else:
        page = 1  # Default to page 1 if it's the first time

    offset = (page - 1) * max_user_per_page

    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        # Get the current user's role and company_id
        cursor.execute("SELECT role, company_id, group_id FROM user WHERE userID=?", (callback_query.from_user.id,))
        user_info = cursor.fetchone()
        role, company_id, group_id = user_info

        if role == "Boss":
            # Boss can see all employees across the company, including their group names
            cursor.execute("""
                SELECT u.id, u.userID, u.userToken, u.fullname, g.group_name, u.role
                FROM user u
                LEFT JOIN user_group g ON u.group_id = g.id
                WHERE u.company_id = ?""", (company_id,))
            employees = cursor.fetchall()
        elif role == "Manager":
            # Manager can only see employees in their group, excluding the manager themselves
            cursor.execute("""
                SELECT u.id, u.userID, u.userToken, u.fullname, u.role
                FROM user u
                WHERE u.company_id = ? AND u.group_id = ?""", (company_id, group_id))
            employees = cursor.fetchall()

    # Filter out the current user and the boss from the employees list
    filtered_employees = [
        employee for employee in employees if employee[1] != callback_query.from_user.id and employee[5] != 'Boss'
    ]

    # Calculate total employees after filtering
    total_employees = len(filtered_employees)

    # Apply pagination after filtering
    paginated_employees = filtered_employees[offset:offset + max_user_per_page]

    # Calculate total pages
    total_pages = (total_employees + max_user_per_page - 1) // max_user_per_page

    # Build the inline keyboard with employee buttons and pagination
    employee_buttons = []
    for employee in paginated_employees:
        employee_id, employee_userID, employee_userToken, employee_fullname = employee[:4]

        # For Boss, show userToken, fullname, and group_name; for Manager, just userToken and fullname
        if role == "Boss":
            group_name = employee[4] if employee[4] else "Без отдела"
            employee_text = f"{employee_userToken} {employee_fullname} - {group_name}"
        else:
            employee_text = f"{employee_userToken} {employee_fullname}"

        employee_buttons.append([InlineKeyboardButton(text=employee_text, callback_data=f"employee_{employee_id}")])

    # Add pagination buttons if necessary
    navigation_buttons = []
    if page > 1:
        navigation_buttons.append(InlineKeyboardButton(text="⬅️ Предыдущая", callback_data=f"list_of_employees_page_{page - 1}"))
    if page < total_pages:
        navigation_buttons.append(InlineKeyboardButton(text="Следующая ➡️", callback_data=f"list_of_employees_page_{page + 1}"))

    if navigation_buttons:
        employee_buttons.append(navigation_buttons)  # Add pagination buttons
    employee_buttons.append([InlineKeyboardButton(text="Назад в главное меню", callback_data="back_to_main_menu")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=employee_buttons)

    if total_employees == 0:
        await callback_query.message.edit_text("В вашем отделе пока нет сотрудников кроме вас.", reply_markup=keyboard)
    else:
        await callback_query.message.edit_text(f"Список сотрудников (Страница {page}/{total_pages}):", reply_markup=keyboard)


@router.callback_query(lambda call: call.data.startswith("task_list"))
async def show_task_list(callback_query: types.CallbackQuery, state: FSMContext):
    if "page" in callback_query.data:
        page = int(callback_query.data.split("_")[-1])
    else:
        page = 1

    offset = (page - 1) * max_task_per_page

    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT role, company_id, group_id FROM user WHERE userID=?", (callback_query.from_user.id,))
        role, company_id, group_id = cursor.fetchone()

        if role == "Boss":
            cursor.execute("""SELECT t.id as task_id, t.task_title, u.userToken, u.fullname, g.group_name
                              FROM task t 
                              LEFT JOIN user u ON t.task_assignee_id = u.id
                              LEFT JOIN user_group g ON u.group_id = g.id 
                              WHERE u.company_id = ? AND t.status != 'Finished'""", (company_id,)) # select all tasks for the company
            tasks = cursor.fetchall()
        elif role == "Manager":
            cursor.execute("""SELECT t.id as task_id, t.task_title, u.userToken, u.fullname, g.group_name
                              FROM task t 
                              LEFT JOIN user u ON t.task_assignee_id = u.id
                              LEFT JOIN user_group g ON u.group_id = g.id 
                              WHERE u.company_id = ? AND u.group_id = ? AND t.status != 'Finished'""", (company_id, group_id,)) # select all tasks for the company
            tasks = cursor.fetchall()
        else:
            cursor.execute("""SELECT t.id as task_id, t.task_title, u.userToken, u.fullname, g.group_name
                              FROM task t
                              LEFT JOIN user u ON t.task_assignee_id = u.id
                              LEFT JOIN user_group g ON u.group_id = g.id
                              WHERE u.id = ?""", (callback_query.from_user.id,))
            tasks = cursor.fetchall()

    total_tasks = len(tasks)

    paginated_tasks = tasks[offset:offset + max_task_per_page]

    total_pages = (total_tasks + max_task_per_page - 1) // max_task_per_page

    task_buttons = []
    if role == "Boss" or role == "Manager":
        task_buttons.append([InlineKeyboardButton(text="Создать задачу", callback_data="create_task")])

    for task in paginated_tasks:
        task_id, task_title, userToken, fullname, group_name = task[:5]

        if role == "Boss":
            task_text = f"'{group_name}' {userToken} {fullname} - {task_title}"
        elif role == "Manager":
            task_text = f"{userToken} {fullname} - {task_title}"
        else:
            task_text = f"{task_title}"
        
        task_buttons.append([InlineKeyboardButton(text=task_text, callback_data=f"task_{task_id}")])

    navigation_buttons = []
    if page > 1:
        navigation_buttons.append(InlineKeyboardButton(text="⬅️ Предыдущая", callback_data=f"task_list_page_{page - 1}"))
    if page < total_pages:
        navigation_buttons.append(InlineKeyboardButton(text="Следующая ➡️", callback_data=f"task_list_page_{page + 1}"))

    if navigation_buttons:
        task_buttons.append(navigation_buttons)  # Add pagination buttons
    task_buttons.append([InlineKeyboardButton(text="Назад в главное меню", callback_data="back_to_main_menu")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=task_buttons)

    if total_tasks == 0:
        if role == "Boss":
            await callback_query.message.edit_text("В вашей компании пока нет задач.", reply_markup=keyboard)
        elif role == "Manager":
            await callback_query.message.edit_text("В вашем отделе пока нет задач.", reply_markup=keyboard)
        else:
            await callback_query.message.edit_text("У вас пока нет задач.", reply_markup=keyboard)
    else:
        if role == "Boss":
            await callback_query.message.edit_text(f"Список незавершенные задач в вашей компании:\n\nЧисло всего задач: {total_tasks}\nСтраница {page}/{total_pages}", reply_markup=keyboard)
        elif role == "Manager":
            await callback_query.message.edit_text(f"Список незавершенные задач в вашем отделе:\n\nЧисло всего задач: {total_tasks}\nСтраница {page}/{total_pages}", reply_markup=keyboard)
        else:
            await callback_query.message.edit_text(f"Ваши незавершенные задачи:\n\nЧисло всего задач: {total_tasks}\nСтраница {page}/{total_pages}", reply_markup=keyboard)