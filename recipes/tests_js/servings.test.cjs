const test = require("node:test");
const assert = require("node:assert/strict");

const { formatAmount, scaleAmount } = require("../static/recipes/js/servings.js");

test("scales an ingredient from its base serving count", () => {
    assert.equal(scaleAmount(1.5, 6, 4), 2.25);
    assert.equal(scaleAmount(400, 2, 4), 200);
});

test("formats common fractions and mixed numbers", () => {
    assert.equal(formatAmount(0.5), "1/2");
    assert.equal(formatAmount(1.25), "1 1/4");
    assert.equal(formatAmount(2.666), "2 2/3");
});

test("uses a concise decimal when no common fraction is close", () => {
    assert.equal(formatAmount(1.1), "1.1");
    assert.equal(formatAmount(2), "2");
});
