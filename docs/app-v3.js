(function (root) {
  "use strict";

  const LABELS = ["RENDAH", "SEDANG", "TINGGI"];
  const RISK_INFO = {
    TINGGI: {
      title: "Perlu pemeriksaan lebih lanjut",
      recommendations: [
        "Pastikan aktivitas dilakukan oleh pengguna yang sah.",
        "Periksa log autentikasi dan waktu kejadian.",
        "Jika aktivitas tidak dikenal, hubungi administrator.",
      ],
    },
    SEDANG: {
      title: "Perlu diverifikasi",
      recommendations: [
        "Konfirmasi apakah perangkat dan waktu akses wajar.",
        "Tinjau riwayat login terkait.",
        "Aktifkan autentikasi multifaktor jika tersedia.",
      ],
    },
    RENDAH: {
      title: "Tidak banyak indikator risiko pada input",
      recommendations: [
        "Tetap gunakan kata sandi unik dan autentikasi multifaktor.",
        "Pantau aktivitas dan peringatan keamanan lainnya.",
      ],
    },
  };

  function predictRisk(model, features) {
    if (!model || !Array.isArray(model.trees) || model.trees.length === 0) {
      throw new Error("File model tidak memiliki pohon Random Forest.");
    }
    if (!Array.isArray(features) || features.length !== model.features.length) {
      throw new Error("Jumlah indikator tidak sesuai dengan fitur model.");
    }

    const probabilities = model.classes.map(() => 0);
    for (const tree of model.trees) {
      let node = 0;
      while (tree.feature[node] >= 0) {
        const featureIndex = tree.feature[node];
        node = features[featureIndex] <= tree.threshold[node]
          ? tree.left[node]
          : tree.right[node];
      }
      const leafValues = tree.values[node];
      const total = leafValues.reduce((sum, value) => sum + value, 0);
      if (total <= 0) {
        throw new Error("Model memiliki daun tanpa sampel.");
      }
      for (let classIndex = 0; classIndex < probabilities.length; classIndex += 1) {
        probabilities[classIndex] += leafValues[classIndex] / total / model.trees.length;
      }
    }

    let predictedIndex = 0;
    for (let index = 1; index < probabilities.length; index += 1) {
      if (probabilities[index] > probabilities[predictedIndex]) {
        predictedIndex = index;
      }
    }
    const roundedProbabilities = probabilities.map((value) => Number(value.toFixed(4)));
    return {
      level: model.classes[predictedIndex],
      score: roundToEven(roundedProbabilities[predictedIndex] * 100),
      probabilities: Object.fromEntries(
        model.classes.map((label, index) => [label, roundedProbabilities[index]]),
      ),
    };
  }

  function roundToEven(value) {
    const lower = Math.floor(value);
    const fraction = value - lower;
    if (Math.abs(fraction - 0.5) < 1e-10) {
      return lower % 2 === 0 ? lower : lower + 1;
    }
    return Math.round(value);
  }

  function buildAnalysis(input, prediction) {
    const details = [
      ["Percobaan login gagal", String(input.failedLogins)],
      ["Perangkat belum dikenal", input.unknownDevice ? "Ya" : "Tidak"],
      ["Waktu akses tidak biasa", input.unusualTime ? "Ya" : "Tidak"],
      ["Akses ke bagian sensitif", input.sensitiveAccess ? "Ya" : "Tidak"],
    ];
    const reasons = [];
    if (input.failedLogins > 0) {
      reasons.push(`Terdapat ${input.failedLogins} percobaan login gagal.`);
    }
    if (input.unknownDevice) {
      reasons.push("Akses berasal dari perangkat yang belum dikenal.");
    }
    if (input.unusualTime) {
      reasons.push("Akses terjadi pada waktu yang tidak biasa.");
    }
    if (input.sensitiveAccess) {
      reasons.push("Aktivitas menyentuh bagian atau data sensitif.");
    }
    if (reasons.length === 0) {
      reasons.push("Tidak ada indikator tambahan yang dipilih.");
    }

    return {
      ...prediction,
      title: RISK_INFO[prediction.level].title,
      details,
      reasons,
      recommendations: RISK_INFO[prediction.level].recommendations,
    };
  }

  function renderList(target, items, details) {
    target.replaceChildren();
    for (const item of items) {
      const li = document.createElement("li");
      if (details) {
        const strong = document.createElement("strong");
        strong.textContent = `${item[0]}: `;
        li.append(strong, document.createTextNode(item[1]));
      } else {
        li.textContent = item;
      }
      target.append(li);
    }
  }

  function renderResult(input, result) {
    const riskCard = document.getElementById("risk-card");
    riskCard.className = `risk risk-${result.level.toLowerCase()}`;
    document.getElementById("risk-level").textContent = result.level;
    document.getElementById("risk-title").textContent = result.title;
    document.getElementById("risk-meter").style.width = `${result.score}%`;
    document.getElementById("risk-score").textContent =
      `Probabilitas kelas terpilih: ${result.score}% · bukan kepastian serangan`;

    const probabilities = document.getElementById("probabilities");
    probabilities.replaceChildren();
    for (const label of LABELS) {
      const value = result.probabilities[label] * 100;
      const row = document.createElement("div");
      row.className = "bar-row";
      const barLabel = document.createElement("div");
      barLabel.className = "bar-label";
      const name = document.createElement("span");
      name.textContent = label;
      const percentage = document.createElement("strong");
      percentage.textContent = `${value.toFixed(2)}%`;
      barLabel.append(name, percentage);
      const track = document.createElement("div");
      track.className = "bar-track";
      const fill = document.createElement("div");
      fill.className = `bar-fill bar-${label.toLowerCase()}`;
      fill.style.width = `${value}%`;
      track.append(fill);
      row.append(barLabel, track);
      probabilities.append(row);
    }

    renderList(document.getElementById("indicator-list"), result.details, true);
    renderList(document.getElementById("reasons-list"), result.reasons);
    renderList(document.getElementById("recommendations-list"), result.recommendations);
    const inputSummary = (
      `${input.failedLogins} percobaan login gagal; perangkat belum dikenal: ` +
      `${input.unknownDevice ? "Ya" : "Tidak"}; waktu akses tidak biasa: ` +
      `${input.unusualTime ? "Ya" : "Tidak"}; akses ke bagian sensitif: ` +
      `${input.sensitiveAccess ? "Ya" : "Tidak"}.`
    );
    document.getElementById("explanation").textContent =
      `Dari input yang kamu berikan, tercatat ${inputSummary} ` +
      `Model ML memprediksi tingkat risiko ${result.level} ` +
      `(probabilitas kelas ${result.score}%). Prediksi ini mempertimbangkan: ` +
      `${result.reasons.join("; ")} Saran sesuai hasil tersebut: ` +
      `${result.recommendations.join("; ")} ` +
      "Prediksi ini adalah informasi pendukung, bukan kepastian adanya serangan.";

    document.getElementById("empty-result").hidden = true;
    document.getElementById("result-content").hidden = false;
    document.getElementById("summary-level").textContent = result.level;
    document.getElementById("summary-score").textContent =
      `Probabilitas kelas ${result.score}%`;
  }

  async function initialize() {
    const status = document.getElementById("model-status");
    const systemStatus = document.getElementById("system-status");
    const error = document.getElementById("analysis-error");
    const form = document.getElementById("analysis-form");
    const button = document.getElementById("analyze-button");
    let model;
    let analysisCount = 0;

    try {
      const response = await fetch("model.json");
      if (!response.ok) {
        throw new Error(`Model gagal dimuat (HTTP ${response.status}).`);
      }
      model = await response.json();
      if (model.algorithm !== "RandomForestClassifier") {
        throw new Error("Algoritma pada file model tidak sesuai.");
      }
      status.textContent = "● Model terlatih v3 siap";
      systemStatus.textContent = "Siap dianalisis";
      document.getElementById("system-caption").textContent =
        `${model.trees.length} pohon model dimuat di browser`;
      button.disabled = false;
    } catch (exception) {
      status.textContent = "● Model gagal dimuat";
      systemStatus.textContent = "Model tidak tersedia";
      error.textContent = `${exception.message} Muat ulang halaman atau periksa file model.`;
      error.hidden = false;
    }

    form.addEventListener("submit", (event) => {
      event.preventDefault();
      error.hidden = true;
      const failedLogins = Number(document.getElementById("failed-logins").value);
      if (!Number.isInteger(failedLogins) || failedLogins < 0 || failedLogins > 100000) {
        error.textContent = "Masukkan jumlah percobaan login sebagai bilangan bulat antara 0 dan 100000.";
        error.hidden = false;
        return;
      }

      const input = {
        failedLogins,
        unknownDevice: form.elements.unknown_device.value === "yes",
        unusualTime: form.elements.unusual_time.value === "yes",
        sensitiveAccess: form.elements.sensitive_access.value === "yes",
      };
      const features = [
        input.failedLogins,
        Number(input.unknownDevice),
        Number(input.unusualTime),
        Number(input.sensitiveAccess),
      ];
      try {
        const prediction = predictRisk(model, features);
        const result = buildAnalysis(input, prediction);
        renderResult(input, result);
        analysisCount += 1;
        document.getElementById("analysis-count").textContent = String(analysisCount);
      } catch (exception) {
        error.textContent = `Analisis gagal: ${exception.message}`;
        error.hidden = false;
      }
    });
  }

  const api = { predictRisk, buildAnalysis };
  root.AICyberIntelligence = api;
  if (typeof module !== "undefined" && module.exports) {
    module.exports = api;
  }
  if (typeof document !== "undefined") {
    document.addEventListener("DOMContentLoaded", initialize);
  }
})(typeof globalThis !== "undefined" ? globalThis : this);
