def get_securities_in_portfolios_by_user(user):
    return [i.security for i in user.securities.all()]


def get_followed_securities_by_user(user, exclude_portfolios=True):
    result = user.security_followed.all()
    if exclude_portfolios:
        security_in_portfolios = user.securities.all().values('security')
        result = result.exclude(id__in=security_in_portfolios)
    return result
