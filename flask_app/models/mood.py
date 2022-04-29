from flask_app.config.mysqlconnection import connectToMySQL

class Mood:
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.energy = data['energy']
        self.dance = data['dance']
        self.valence = data['valence']
        self.bg_img = data['bg_img']
        self.genres = data['genres']

    @classmethod
    def create_mood(cls, data):
    
        query = 'INSERT INTO moods (name, energy, dance, valence, bg_img, genres) VALUES (%(name)s, %(energy)s, %(dance)s, %(valence)s, %(bg_img)s, %(genres)s);'

        result = connectToMySQL('moods_schema').query_db(query, data)

        return result

    @classmethod
    def get_all_moods(cls):
        query = 'SELECT * FROM moods'

        results = connectToMySQL('moods_schema').query_db(query)

        moods = []

        for item in results:
            moods.append(item)

        return moods

    @classmethod
    def get_mood_by_id(cls, data):
        query = 'SELECT * FROM moods WHERE id = %(mood_id)s'

        result = connectToMySQL('moods_schema').query_db(query, data)

        if len(result) < 1:
            return False
        return cls(result[0])

    @classmethod
    def delete_mood(cls, data):
        query = 'DELETE FROM moods WHERE id = %(mood_id)s;'

        connectToMySQL('moods_schema').query_db(query, data)

    @classmethod
    def update_mood(cls, data):
        query = 'UPDATE moods SET name = %(name)s, energy = %(energy)s, dance = %(dance)s, valence = %(valence)s, bg_img = %(bg_img)s, genres = %(genres)s  WHERE id = %(mood_id)s;'

        result = connectToMySQL('moods_schema').query_db(query, data)

        return result

    

