



# For lowercase tokenization and case-insensitive search
CONFIDENCE_MATRIX_SETTINGS = {
  "settings":{
    "index":{
      "analysis":{
        "analyzer":{
          "analyzer_case_insensitive":{
            "tokenizer":"keyword",
            "filter":"lowercase"
          }
        }
      }
    }
}}