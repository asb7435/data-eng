-- crawler_pipeline.py 실행 전, shop 데이터베이스에 실행한다.
CREATE TABLE IF NOT EXISTS quotes (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    author VARCHAR(100) NOT NULL,
    quote_text VARCHAR(600) NOT NULL,
    tags TEXT NOT NULL,
    crawled_at DATETIME NOT NULL,
    CONSTRAINT uq_quotes_author_text UNIQUE (author, quote_text)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
