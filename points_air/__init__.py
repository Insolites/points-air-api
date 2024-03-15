import uvicorn


def main():
    """Fonction principale"""
    from .api import apiv1
    uvicorn.run(apiv1, port=8000)


if __name__ == '__main__':
    main()
