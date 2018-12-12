import pandas as pd
import pyfpgrowth


def main():

    # Intialize the database connection and the list of years for which data is available
    db_connection = "mysql+pymysql://root@localhost/data_mining_bus_delays"
    toronto_bus_data_years = ["2014", "2015", "2016", "2017", "2018"]

    previous_years_frequent_patterns = {}
    frequent_pattern_min_sup = 25

    # Gather each year's frequent bus delay patterns and store them in "all_years_frequent_patterns"
    # for analysis on interesting patterns
    for year in toronto_bus_data_years:
        # Gather the dataframe representing "that year's" bus delay data
        df_year = pd.read_sql('SELECT * from delays_binned where year = ' + year, db_connection)

        # Pyfpgrowth uses strings -> convert the types accordingly
        df_year['year'] = df_year['year'].apply(str)
        df_year['Route'] = df_year['Route'].apply(str)
        df_year['report_date'] = df_year['report_date'].apply(str)

        # Remove "uninteresting" columns from potential "interesting" datasets
        df_year_filtered = df_year.drop(columns=['index', 'delay_id', 'year', 'report_date', 'Direction', 'Route'])
        df_year_frequent_patterns = pyfpgrowth.find_frequent_patterns(df_year_filtered.values, frequent_pattern_min_sup)
        previous_years_frequent_patterns[year] = df_year_frequent_patterns

    # Create the "future year's" patterns and remove the "future year's" patterns
    # from the previous_year_list_frequent_pattern
    future_year = "2018"
    future_year_frequent_patterns = {future_year: previous_years_frequent_patterns[future_year]}
    del previous_years_frequent_patterns[future_year]

    # Find out the interesting rules between previous data and "future" data
    find_similarities_and_differences(previous_years_frequent_patterns, future_year_frequent_patterns)


# Find all the similar patterns with a "frequent_pattern_minimum_length" of N where previous year's patterns
# are indicative of patterns in a future year
# TODO: This function (or another function) should also look for interesting outlier patterns in ANY year
def find_similarities_and_differences(previous_years_frequent_patterns, future_year_frequent_patterns):

    frequent_pattern_min_length = 5

    for fut_year, fut_frequent_patterns in future_year_frequent_patterns.items():
        for fut_pattern, fut_count in fut_frequent_patterns.items():

            # Patterns predicting future patterns
            predicted_patterns = []
            predicted_patterns_count = []
            predicted_patterns_year = []

            for prev_year, prev_frequent_patterns in previous_years_frequent_patterns.items():
                for prev_pattern, prev_count in prev_frequent_patterns.items():
                    if sorted(fut_pattern) == sorted(prev_pattern) and len(fut_pattern) >= frequent_pattern_min_length:
                        predicted_patterns.append(prev_pattern)
                        predicted_patterns_count.append(prev_count)
                        predicted_patterns_year.append(prev_year)

            if predicted_patterns:
                print("Future Year {} - {}:{} predicted by:".format(fut_year, fut_pattern, fut_count))
                for i in range(len(predicted_patterns)):
                    print("{}:{} - {}".format(predicted_patterns[i], predicted_patterns_count[i], predicted_patterns_year[i]))
                print("-" * 50)


# Finds the frequent patterns greater than or equal to the user's min_sup
# AND patterns which exist in every year in the data set
def find_similar_frequent_patterns(frequent_patterns):
    while True:
        try:
            min_sup = int(input("Enter a min_sup value"))
            print("Printing patterns of length {}".format(min_sup))

            for p in frequent_patterns:
                if len(p) >= min_sup:
                    print("{}: {}".format(p, frequent_patterns[p]))
        except:
            pass


if __name__ == '__main__':
    main()
