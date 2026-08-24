from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw" / "banking77"
PROCESSED_DIR = ROOT / "data" / "processed" / "banking77"
FIGURES_DIR = ROOT / "reports" / "figures"


def load_split(name: str) -> pd.DataFrame:
    path = RAW_DIR / f"{name}.csv"
    df = pd.read_csv(path)
    expected_columns = ["text", "category"]

    if list(df.columns) != expected_columns:
        raise ValueError(f"{path} precisa ter as colunas {expected_columns}")

    return df


def describe_split(name: str, df: pd.DataFrame) -> dict[str, object]:
    text_clean = df["text"].astype(str).str.strip()

    return {
        "split": name,
        "shape": df.shape,
        "dtypes": df.dtypes.astype(str).to_dict(),
        "missing": df.isna().sum().to_dict(),
        "duplicated_rows": int(df.duplicated().sum()),
        "duplicated_texts": int(text_clean.duplicated().sum()),
        "empty_texts": int(text_clean.eq("").sum()),
        "texts_with_outer_spaces": int(df["text"].astype(str).ne(text_clean).sum()),
        "categories": int(df["category"].nunique()),
        "min_per_category": int(df["category"].value_counts().min()),
        "max_per_category": int(df["category"].value_counts().max()),
        "text_length": text_clean.str.len().describe().round(2).to_dict(),
    }


def clean_data(train: pd.DataFrame, test: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, int]]:
    train_clean = train.copy()
    test_clean = test.copy()

    train_clean["text"] = train_clean["text"].astype(str).str.strip()
    test_clean["text"] = test_clean["text"].astype(str).str.strip()
    train_clean = train_clean[["text", "category"]]
    test_clean = test_clean[["text", "category"]]

    duplicate_train_rows = int(train_clean.duplicated().sum())
    duplicate_test_rows = int(test_clean.duplicated().sum())

    train_clean = train_clean.drop_duplicates().reset_index(drop=True)
    test_clean = test_clean.drop_duplicates().reset_index(drop=True)

    test_keys = test_clean["text"].str.lower()
    train_keys = train_clean["text"].str.lower()
    overlap_mask = train_keys.isin(test_keys)
    overlap_count = int(overlap_mask.sum())

    train_clean = train_clean.loc[~overlap_mask].reset_index(drop=True)

    cleaning_stats = {
        "duplicate_train_rows_after_strip": duplicate_train_rows,
        "duplicate_test_rows_after_strip": duplicate_test_rows,
        "train_test_overlaps_removed_from_train": overlap_count,
    }

    return train_clean, test_clean, cleaning_stats


def plot_category_distribution(train: pd.DataFrame) -> None:
    counts = train["category"].value_counts().sort_values(ascending=True)

    plt.figure(figsize=(10, 18))
    plt.barh(counts.index, counts.values, color="#1f77b4")
    plt.title("Distribuicao das categorias - treino")
    plt.xlabel("Quantidade")
    plt.ylabel("Categoria")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "banking77_category_distribution.png", dpi=160)
    plt.close()


def plot_text_length_distribution(train: pd.DataFrame, test: pd.DataFrame) -> None:
    plt.figure(figsize=(10, 5))
    plt.hist(train["text"].str.len(), bins=35, alpha=0.75, label="treino", color="#1f77b4")
    plt.hist(test["text"].str.len(), bins=35, alpha=0.55, label="teste", color="#ff7f0e")
    plt.title("Tamanho das mensagens")
    plt.xlabel("Caracteres")
    plt.ylabel("Quantidade")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "banking77_text_length_distribution.png", dpi=160)
    plt.close()


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    train = load_split("train")
    test = load_split("test")

    raw_summary = [describe_split("train_raw", train), describe_split("test_raw", test)]
    train_clean, test_clean, cleaning_stats = clean_data(train, test)
    clean_summary = [
        describe_split("train_processed", train_clean),
        describe_split("test_processed", test_clean),
    ]

    train_clean.to_csv(PROCESSED_DIR / "train.csv", index=False)
    test_clean.to_csv(PROCESSED_DIR / "test.csv", index=False)

    plot_category_distribution(train_clean)
    plot_text_length_distribution(train_clean, test_clean)

    print("BANKING77 EDA")
    print(f"Raw train shape: {train.shape}")
    print(f"Raw test shape: {test.shape}")
    print(f"Duplicate train rows removed after strip: {cleaning_stats['duplicate_train_rows_after_strip']}")
    print(f"Duplicate test rows removed after strip: {cleaning_stats['duplicate_test_rows_after_strip']}")
    print(
        "Train/test overlaps removed from train: "
        f"{cleaning_stats['train_test_overlaps_removed_from_train']}"
    )
    print(f"Processed train shape: {train_clean.shape}")
    print(f"Processed test shape: {test_clean.shape}")
    print(f"Categories: {train_clean['category'].nunique()}")
    print("\nRaw summary:")
    for item in raw_summary:
        print(item)
    print("\nProcessed summary:")
    for item in clean_summary:
        print(item)


if __name__ == "__main__":
    main()
