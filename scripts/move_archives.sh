#!/bin/bash

# Move test files
mv /Users/eddiekempe/CodeProjects/Marian/archive/ARCHIVED_*test*.py /Users/eddiekempe/CodeProjects/Marian/tests/archive/
mv /Users/eddiekempe/CodeProjects/Marian/archive/*test_*.py /Users/eddiekempe/CodeProjects/Marian/tests/archive/

# Move source code files
mv /Users/eddiekempe/CodeProjects/Marian/archive/ARCHIVED_*{anthropic_key_retrieval,email_processor,process_emails,read_database,proto_read_gmail,database_util,db_init_util,util_logging,lambda_function,catalog_constants,main}.py /Users/eddiekempe/CodeProjects/Marian/src/archive/

# Move script files
mv /Users/eddiekempe/CodeProjects/Marian/archive/ARCHIVED_*{deploy,layer-test,temp}.sh /Users/eddiekempe/CodeProjects/Marian/scripts/archive/

# Move config files
mv /Users/eddiekempe/CodeProjects/Marian/archive/ARCHIVED_*{dynamodb-cf,lambda-config-cf,lambda-role-cf}.yaml /Users/eddiekempe/CodeProjects/Marian/config/archive/
mv /Users/eddiekempe/CodeProjects/Marian/archive/ARCHIVED_*.sql /Users/eddiekempe/CodeProjects/Marian/config/archive/
mv /Users/eddiekempe/CodeProjects/Marian/archive/ARCHIVED_*prompts.txt /Users/eddiekempe/CodeProjects/Marian/config/archive/

# Move remaining files (databases, etc.)
mv /Users/eddiekempe/CodeProjects/Marian/archive/ARCHIVED_*.{db,zip} /Users/eddiekempe/CodeProjects/Marian/config/archive/
