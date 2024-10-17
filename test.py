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