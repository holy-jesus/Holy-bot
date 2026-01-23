from .auth import auth


@auth.route("/logout", methods=["POST"])
def logout():
    pass
