from linkedin_idea_to_post.linkedin.csv_parser import CsvParser


def main():
    share_file_path = "/Users/angelo.buono/PycharmProjects/linkedin-idea-to-post/data/imports/LinkedIn-Shares-DataExport.csv"
    csv_post_reader = CsvParser(share_file_path)

    parser_result = csv_post_reader.parse_raw_posts()
    print("Errors Found:")
    print(parser_result.parsing_errors)
    print("Raw Posts Found:")
    for raw_post in parser_result.raw_posts:
        print(raw_post)


if __name__ == "__main__":
    main()
