def enmapboxApplicationFactory(enmapBox):
    """
    Returns a list of EnMAPBoxApplications
    :param enmapBox: the EnMAP-Box instance.
    :return: EnMAPBoxApplication | [list-of-EnMAPBoxApplications]
    """

    from enpt_enmapboxapp.enpt_enmapboxapp import EnPTEnMAPBoxApp
    return [EnPTEnMAPBoxApp(enmapBox)]

