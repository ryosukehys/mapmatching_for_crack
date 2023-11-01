import csv
import requests
import pandas as pd

# Mapboxのアクセストークンをセットします。
MAPBOX_ACCESS_TOKEN = "Set Your Token"

# MapboxのマップマッチングAPIのURL
MAPBOX_MATCHING_URL = "https://api.mapbox.com/matching/v5/mapbox/driving/{coordinates}?access_token={access_token}"


def map_match(coordinates):
    """
    Mapbox Map Matching APIを使用して,緯度経度のリストをマップマッチングします.
    coordinates = list(zip(df['latitude'], df['longitude']))
    """
    matched_coordinates = []
    # 100個の座標ごとにバッチを作成します。
    for i in range(0, len(coordinates), 100):
        batch = coordinates[i : i + 100]
        # 緯度経度のペアをセミコロンで区切って文字列に変換します。
        coordinates_str = ";".join([f"{lon},{lat}" for lat, lon in batch])
        # Mapbox Map Matching APIのURLを作成します。
        url = MAPBOX_MATCHING_URL.format(
            coordinates=coordinates_str, access_token=MAPBOX_ACCESS_TOKEN
        )
        # APIを呼び出します。
        response = requests.get(url)
        # 応答をJSONとして解析します。
        match = response.json()
        # マッチした座標をリストに追加します。
        matched_coordinates.extend(
            [
                (trace["location"][1], trace["location"][0])
                for trace in match["tracepoints"]
                if trace is not None
            ]
        )
    return matched_coordinates


def map_match_csv(df, output_csv):
    """
    CSVファイルを読み込み,緯度経度データをマップマッチングし,結果を新しいCSVファイルに出力します.
    """
    # 入力CSVファイルを読み込みます。
    # 緯度経度のペアのリストを作成します。
    coordinates = list(zip(df["latitude"], df["longitude"]))
    # マップマッチングを実行します。
    matched_coordinates = map_match(coordinates)
    # マッチした座標をデータフレームに追加します。
    df["matched_latitude"], df["matched_longitude"] = zip(*matched_coordinates)
    # 結果を新しいCSVファイルに出力します。
    df.to_csv(output_csv, index=False)


def is_convertible(row):
    """
    DataFrameの行が整数に変換できるかどうかを確認します.
    正規に記録できていない値を削除する目的
    """
    try:
        int(row["meshcode"])
        return True
    except ValueError:
        return False


def process_csv(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    mask = df.apply(is_convertible, axis=1)
    df = df[mask].reset_index(drop=True)
    map_match_csv(df, output_csv)
