@app.route('/', methods=['POST'])
def validate_user():

    email = request.form['email']
    password = request.form['password']
    verify_password = request.form['verify']

    password_error = ''
    verify_error = ''
    email_error = ''

    if len(password) < 3 or len(password) > 120 or ' ' in password:
        password_error = 'Password too short/long'

    if verify_password == '':
        verify_error = 'Please retype your password'

    if password != verify_password:
        verify_error = 'Passwords do not match!'
    if email == '':
        email_error = 'Please enter your email address'
    if email != '':
        if len(email) < 3 or len(email) > 120:
            email_error = 'Email too short/long'
        if email.count("@") != 1 or email.count(".") < 1:
            email_error = 'Please enter a valid email'
        if ("@" not in email) or ("." not in email) or (' ' in email):
            email_error = 'Please enter a valid email'

    if not username_error and not password_error and not verify_error and not email_error:
        return render_template("welcome.html", username=username)
    else:
        return render_template('signup_form.html', username=username,
            email=email, username_error=username_error, 
            password_error=password_error, verify_error=verify_error, 
            email_error=email_error)