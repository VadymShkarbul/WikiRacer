# WikiRacering Game
Іmplemented a function that takes two article names (start and end) as parameters and returns a list of page names through which you can get to it, or an empty list if such a path could not be found.
The received link information from the page is stored in a postgres database running in a Docker container
At each next run, connections from the database are used to avoid making the same queries twice.
### Example:
```shell
Input:
(‘Дружба’, ‘Рим’) -> [‘Дружба’, ‘Якопо Понтормо’, ‘Рим’]
```
## Installation:
### [Python 3](https://www.python.org/downloads/) must be already installed
```shell
git clone https://github.com/VadymShkarbul/WikiRacer.git
cd WikiRacer
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
docker-compose up -d
alembic upgrade head
python wikiracing_test.py
```
<img width="1792" alt="" src="https://user-images.githubusercontent.com/111114742/213871913-942dddd1-869f-4f7b-bdbe-aeea57e4572e.png">
