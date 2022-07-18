import json
import sqlite3
from flask import Flask

app = Flask(__name__)


def get_search_db(sql):
    with sqlite3.connect("netflix.db") as connection:
        connection.row_factory = sqlite3.Row
        result = connection.execute(sql).fetchall()

        return result


def get_by_title(title):
    sql = f"""
        SELECT*
        FROM netflix
        WHERE title = '{title}'
        ORDER BY release_year DESC
        LIMIT 1
        """
    result = get_search_db(sql)
    for item in result:
        return dict(item)


@app.route("/movie/<title>")
def search_by_title_view(title):
    result = get_by_title(title=title)
    return app.response_class(
        response=json.dumps(result, ensure_ascii=False, indent=4),
        status=200,
        mimetype="application/json"

    )


@app.route("/movie/<year1>/to/<year2>")
def search_data_view(year1, year2):
    sql = f"""select title, release_year
             from netflix
             where release_year between '{year1}' and '{year2}'
             limit 100
             """
    result = []

    for item in get_search_db(sql=sql):
        result.append(dict(item))
    return app.response_class(
        response=json.dumps(result, ensure_ascii=False, indent=4),
        status=200,
        mimetype="application/json"
    )


@app.route("/rating/<rating>/")
def search_rating(rating):
    my_dict = {
        "children": ("G", "G"),
        "family": ("G", "PG", "PG-13"),
        "adult": ("R", "NC-17")
    }

    sql = f'''
    select*
    from netflix
    where rating in {my_dict.get(rating, ("R", "R"))}
    '''

    result = []

    for item in get_search_db(sql=sql):
        result.append(dict(item))

    return app.response_class(
        response=json.dumps(result, ensure_ascii=False, indent=4),
        status=200,
        mimetype='application/json'
    )


@app.route("/genre/<genre>/")
def search_genre_view(genre):
    sql = f'''
        select*
        from netflix
        where listed_in like "%{genre}"
        order by release_year desc
        limit 10'''

    result = []

    for item in get_search_db(sql=sql):
        result.append(dict(item))

    return app.response_class(
        response=json.dumps(result, ensure_ascii=False, indent=4),
        status=200,
        mimetype='application/json'
    )


def search_double_name(name1, name2):
    sql = f"""
    select "cast"
    from netflix
    where "cast" like "%{name1}%" 
    and "cast" like "%{name2}%"
    """
    result = []
    names_dict = {}
    for item in get_search_db(sql=sql):
        names = set(dict(item).get('cast').split(',')) - set([name1, name2])

        for name in names:
            names_dict[str(name).strip()] = names_dict.get(str(name).strip(), 0) + 1

    for key, value in names_dict.items():
        if value >= 2:
            result.append(key)

    return result


def get_type_year_genre(typ, year, genre):
    sql = f"""
    select title, description, listed_in
    from netflix
    where type = "{typ}"
    and release_year = "{year}"
    and listed_in like "%{genre}%"
    """
    result = []

    for item in get_search_db(sql):
        result.append(dict(item))

    return json.dumps(result, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    print(search_double_name('Rose McIver', 'Ben Lamb'))
    print(get_type_year_genre('Movie', '2021', 'Documentaries'))
    # app.run()
