from dagster import ConfigurableResource
import psycopg2

class PgConnectionRessource(ConfigurableResource):
    host : str
    dbname : str
    port : int
    user : str
    password : str

    def connect_db(self): 
        conn = psycopg2.connect(
            host=self.host,
            dbname=self.dbname,
            port=self.port,
            user=self.user,
            password=self.password
        )
        return conn

