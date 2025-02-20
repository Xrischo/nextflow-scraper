import argparse
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import sys

def fetch_data(db_path, table, x_column, y_column, filters):
    try:
        conn = sqlite3.connect(db_path)
        query = f"SELECT {x_column}, {y_column} FROM {table}"
        if filters:
            query += f" WHERE {filters}"
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df
    except Exception as e:
        print(f"Error generating chart: {e}")
        sys.exit(1)

def generate_chart(df, chart_type, x_column, y_column, output_file):
    plt.figure(figsize=(8, 6))

    if chart_type == "line":
        plt.plot(df[x_column], df[y_column], marker="o", linestyle="-", color="b")
        plt.xlabel(x_column)
        plt.ylabel(y_column)
        plt.title(f"Line Chart: {y_column} vs {x_column}")

    elif chart_type == "bar":
        plt.bar(df[x_column], df[y_column], color="g")
        plt.xlabel(x_column)
        plt.ylabel(y_column)
        plt.title(f"Bar Chart: {y_column} vs {x_column}")

    elif chart_type == "pie":
        plt.pie(df[y_column], labels=df[x_column], autopct="%1.1f%%", startangle=140, colors=plt.cm.Paired.colors)
        plt.title(f"Pie Chart: Distribution of {y_column}")

    else:
        print("Invalid chart type. Choose from 'line', 'bar', or 'pie'")
        sys.exit(1)

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a chart from a database.")
    parser.add_argument("--db", required=True, help="Path to the database file (.db)")
    parser.add_argument("--table", required=True, help="Source table in the database")
    parser.add_argument("--chart", required=True, choices=["line", "bar", "pie"], help="Type of chart to generate")
    parser.add_argument("--x", required=True, help="Column for the X-axis (categories for pie charts)")
    parser.add_argument("--y", required=True, help="Column for the Y-axis (values for pie charts)")
    parser.add_argument("--filter", default="", help="SQL filter condition (e.g., 'date > \'2025-02-01\'') (note the quotes around the date)")
    parser.add_argument("--output", default="chart.png", help="Output image file (default: chart.png)")

    args = parser.parse_args()

    data = fetch_data(args.db, args.table, args.x, args.y, args.filter)
    generate_chart(data, args.chart, args.x, args.y, args.output)