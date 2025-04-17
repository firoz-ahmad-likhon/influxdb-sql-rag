class Prompt:
    """Prompt class for generating prompts for different tasks."""

    @staticmethod
    def sql_query_generation() -> str:
        """Prompt for SQL query generation."""
        return """Given an input question, create a syntactically correct sql query to run in InfluxDB 3 to help find the answer. The sql syntax must be compatible with InfluxDB 3. Unless the user specifies in his question a specific number of examples they wish to obtain, always limit your query to at most {top_k} results. You can order the results by a relevant column to return the most interesting examples in the database.
        Never query for all the columns from a specific table, only ask for a the few relevant columns given the question.
        Pay attention to use only the column names that you can see in the schema description. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.

        Only use the following tables:
        {table_info}

        Only use the following tables and their corresponding columns:
        {column_info}

        Here are sample data for each table:
        {sample_data}

        Here are some errors you should not repeat again, if any:
        {error_list}
        """

    @staticmethod
    def answer_machine() -> str:
        """Prompt for answer of a question.."""
        return """"You are an expert answering machine.
        Given the following user question, corresponding SQL query, and SQL result, answer the user question in natural language.
        Question: {question}
        SQL Query: {query}
        SQL Result: {result}
        """

    @staticmethod
    def normal_chat() -> str:
        """Prompt for normal chat."""
        return """The user asked: {question}
        This question is not related to the database or requires data we don't have.
        Please provide a helpful response without referring to database queries.
        If there was an error, it was: {error}
        """

    @staticmethod
    def database_usability() -> str:
        """Prompt for checking if process uses database."""
        return """You are an expert at determining if a question requires database access.
        We have an InfluxDB database with the following tables and columns:
        {columns}

        You must return either TRUE or FALSE.
        A question requires database access if:
        1. It mentions any table or column name exactly OR partially (e.g., ''humidity'' ~ 'hum')
        2. It contains words that are **synonyms or similar in meaning** to the table or column names (e.g., via cosine similarity or common usage)
        3. It asks about previous query results

        Return FALSE if:
        1. The question is about general knowledge, programming help, or anything unrelated to querying the database.
        """

    @staticmethod
    def follow_up() -> str:
        """Prompt for follow-up conversation."""
        return """The user asked: {question}
        This appears to be a request to see the previous query results in a different format.

        The previous query was: {query}
        The query results are: {result}

        Please present this data as requested by the user. If they want a table format, show all the data in a clean tabular format without summarizing. If they're asking a follow-up question about the data, answer it based on the provided results.

        Display ALL the data in the format requested by the user. DO NOT summarize the data unless explicitly asked to do so.
        """
