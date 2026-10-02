BENCHMARK = [
    {
        "question": "What does it mean that Python is a high-level language?",
        "expected_facts": [
            ["python", "high-level"],
            ["abstraction", "low-level-details"],
        ],
        "relevant_pages": [7],
    },
    {
        "question": "What are the three programming paradigms supported by Python?",
        "expected_facts": [
            ["procedural"],
            ["object-oriented"],
            ["functional"],
        ],
        "relevant_pages": [9],
    },
    {
        "question": "What is the difference between a compiler and an interpreter?",
        "expected_facts": [
            ["compiler", "translates-before-execution"],
            ["interpreter", "executes-during-translation"],
        ],
        "relevant_pages": [16],
    },
    {
        "question": "What are the five kinds of literals in Python?",
        "expected_facts": [
            ["numeric"],
            ["string"],
            ["boolean"],
            ["collection"],
            ["special"],
        ],
        "relevant_pages": [33],
    },
    {
        "question": "How is None different from zero?",
        "expected_facts": [
            ["none", "absence-of-value"],
            ["zero", "numeric-value"],
        ],
        "relevant_pages": [34, 44],
    },
    {
        "question": "What does it mean that strings are immutable?",
        "expected_facts": [
            ["strings", "immutable"],
            ["cannot-modify-existing-string"],
        ],
        "relevant_pages": [50],
    },
    {
        "question": "How does string slicing work in Python?",
        "expected_facts": [
            ["slicing", "portion-of-string"],
            ["start", "stop"],
        ],
        "relevant_pages": [52, 53],
    },
    {
        "question": "What is the difference between append and extend?",
        "expected_facts": [
            ["append", "single-element"],
            ["extend", "multiple-elements"],
        ],
        "relevant_pages": [64],
    },
    {
        "question": "What is the difference between a tuple, set, and dictionary?",
        "expected_facts": [
            ["tuple", "ordered"],
            ["set", "unique"],
            ["dictionary", "key-value"],
        ],
        "relevant_pages": [76, 77],
    },
    {
        "question": "Why is the stop value excluded when using range?",
        "expected_facts": [
            ["stop", "excluded"],
            ["range", "starts-before-stop"],
        ],
        "relevant_pages": [81, 82],
    },
]