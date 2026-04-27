function calculate() {
    let S = parseFloat(document.getElementById('S').value) / 100;
    let R = parseFloat(document.getElementById('R').value) / 100;
    let S1 = parseFloat(document.getElementById('S1').value) / 100;
    let S2 = parseFloat(document.getElementById('S2').value) / 100;
    let R1 = parseFloat(document.getElementById('R1').value) / 100;
    let R2 = parseFloat(document.getElementById('R2').value) / 100;
    let W1 = Math.sqrt(S * (1 - R));
    let W2 = Math.sqrt(R * (1 - S));
    let P1 = ((S1 * (1 - R2)) / W1) / (((S1 * (1 - R2)) / W1) + ((1 - S1) * R2) / W2);
    let P2 = ((S2 * (1 - R1)) / W2) / (((S2 * (1 - R1)) / W2) + ((1 - S2) * R1) / W1);
    document.getElementById('prob_display').innerText = (P1 * 100).toFixed(2) + "%";
}
