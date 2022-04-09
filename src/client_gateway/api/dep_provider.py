from services.stream_database import StreamDatabase

class DepProvider():

    _streams_db = None

    @staticmethod
    def get_streams_db():
        if not hasattr(DepProvider, '_streams_db') or DepProvider._streams_db == None:
            DepProvider._streams_db = StreamDatabase()

        return DepProvider._streams_db
