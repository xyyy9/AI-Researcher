python3 src/lit_review.py \
 --topic_description "novel prompting methods that can improve factuality and reduce hallucination of large language models" \
 --cache_name "factuality_prompting" \
 --track "method" \
 --max_paper_bank_size 70 \
 --print_all

python3 src/lit_review.py \
 --topic_description "novel methods that can better quantify uncertainty or calibrate the confidence of large language model" \
 --cache_name "uncertainty" \
 --track "method" \
 --max_paper_bank_size 70 \
 --print_all

python3 src/lit_review.py \
 --topic_description "novel prompting methods to jailbreak or adversarially attack large language models as a way to identify their vulnerabilities" \
 --cache_name "adversarial_attack" \
 --track "method" \
 --max_paper_bank_size 70 \
 --print_all

python3 src/lit_review.py \
 --topic_description "probing social biases and fairness issues of large language models through prompting" \
 --cache_name "bias" \
 --track "analysis" \
 --max_paper_bank_size 70 \
 --print_all
 