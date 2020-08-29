def get_portfolios_by_user(user):
    return user.portfolios.all()


def get_followed_portfolios_by_user(user):
    return user.portfolio_followed.all()
