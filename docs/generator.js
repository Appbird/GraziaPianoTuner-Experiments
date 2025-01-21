// 対応表のデータ
const mapping = {
    "春": "spring",
    "明るさ": "brightness",
    "厳かな": "solemn",
    "気まぐれな": "capricious",
    "勇敢な(case 1)": "brave1",
    "勇敢な(case 2)": "brave2",
    "堂々とした(case 1)": "dignified1",
    "堂々とした(case 2)": "dignified2",
    "静かな": "quiet",
    "沈んだ": "sank",
    "クラシック感(case 1)": "classic1",
    "クラシック感(case 2)": "classic2",
    "ジャズ感(case 1)": "jazz1",
    "ジャズ感(case 2)": "jazz2",
    "スイング感(case 1)": "swing1",
    "スイング感(case 2)": "swing2"
};

// テーブルのtbodyを取得
const tbody = document.querySelector("#music-table tbody");

// 対応表を基にテーブルを生成
Object.entries(mapping).forEach(([axisName, fileName]) => {
    // 新しい行を作成
    const row = document.createElement("tr");

    // 軸の名前のセル
    const axisCell = document.createElement("td");
    axisCell.textContent = axisName;
    row.appendChild(axisCell);

    // 0, 0.5, 1の音声ファイルセルを作成
    [0, 5, 10].forEach(value => {
        const cell = document.createElement("td");
        const audio = document.createElement("audio");
        audio.controls = true;
        const source = document.createElement("source");
        source.src = `music/${fileName}-${value.toString().padStart(2, "0")}.mp3`;
        source.type = "audio/mpeg";
        audio.appendChild(source);
        cell.appendChild(audio);
        row.appendChild(cell);
    });

    // 行をtbodyに追加
    tbody.appendChild(row);
});
