from project import app
import os

false_in_production = os.environ.get('ENV') != 'production'

if __name__ == '__main__':
    app.run(port=3000)