import uvicorn


def main():
    """Fonction principale"""
    from .api import app
    uvicorn.run(app, port=8092)


if __name__ == '__main__':
    main()
