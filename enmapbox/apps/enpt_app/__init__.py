def enmapboxApplicationFactory(enmapBox):
    """
    Returns a list of EnMAPBoxApplications
    :param enmapBox: the EnMAP-Box instance.
    :return: EnMAPBoxApplication | [list-of-EnMAPBoxApplications]
    """


    from enpt_enmapboxapp.enpt_enmapboxapp import EnPTEnMAPBoxApp

    # returns a list of EnMAP-Box Applications. Usually only one is returned,
    # but you might provide as many as you like.
    return [EnPTEnMAPBoxApp(enmapBox)]