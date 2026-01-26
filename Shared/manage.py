import typer

app = typer.Typer()


@app.command()
def create_admin():
    pass


@app.command()
def create_user():
    pass


@app.command()
def unban():
    pass


@app.command()
def ban():
    pass


@app.command()
def delete_user():
    pass


@app.command()
def make_admin():
    pass


if __name__ == "__main__":
    app()
