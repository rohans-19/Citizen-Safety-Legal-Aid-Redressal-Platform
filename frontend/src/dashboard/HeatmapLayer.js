/**
 * HeatmapLayer.js — Member C
 * D3.js Karnataka district choropleth map driven by T-GAT anomaly scores.
 * Colors: green (LOW) → amber (MEDIUM) → red (HIGH)
 * Emits onDistrictHover(districtName, mouseX, mouseY) for tooltip.
 * GeoJSON is loaded from /karnataka_geojson.json via Vite public folder.
 */
import React, { useEffect, useRef } from "react";
import * as d3 from "d3";

// GeoJSON uses legacy district names — map to our analytics names (bidirectional)
const GEO_TO_ANALYTICS = {
  "Bagalkot":       "Bagalkote",
  "Bangalore Rural":"Bengaluru Rural",
  "Bangalore Urban":"Bengaluru Urban",
  "Belgaum":        "Belagavi",
  "Bellary":        "Ballari",
  "Bijapur":        "Vijayapura",
  "Chamrajnagar":   "Chamarajanagar",
  "Chikmagalur":    "Chikkamagaluru",
  "Dakshin Kannad": "Dakshina Kannada",
  "Gulbarga":       "Kalaburagi",
  "Mysore":         "Mysuru",
  "Shimoga":        "Shivamogga",
  "Tumkur":         "Tumakuru",
  "Uttar Kannand":  "Uttara Kannada",
};

// Resolve a GeoJSON district name to our analytics key
function resolveDistrict(geoName) {
  return GEO_TO_ANALYTICS[geoName] || geoName;
}

// Tier → fill color mapping
const TIER_FILL = {
  HIGH:   "#ef4444",
  MEDIUM: "#f59e0b",
  LOW:    "#22c55e",
};
const DEFAULT_FILL = "#1e3a5f";
const STROKE       = "#0f172a";
const HOVER_STROKE = "#f8fafc";

export default function HeatmapLayer({ scoreData, onDistrictHover, onDistrictLeave }) {
  const svgRef = useRef(null);

  useEffect(() => {
    // Load Karnataka GeoJSON once
    fetch("/karnataka_geojson.json")
      .then((r) => r.json())
      .then((geo) => renderMap(geo))
      .catch((e) => console.error("[HeatmapLayer] GeoJSON load failed:", e));
  }, []);

  // Re-color districts when scoreData changes
  useEffect(() => {
    if (!svgRef.current || !scoreData) return;
    const svg = d3.select(svgRef.current);
    svg.selectAll("path.district").attr("fill", (d) => {
      const raw  = d.properties?.NAME_2 || d.properties?.district || d.properties?.DISTRICT || "";
      const name = resolveDistrict(raw);
      const info = scoreData[name];
      return info ? TIER_FILL[info.tier] || DEFAULT_FILL : DEFAULT_FILL;
    });
  }, [scoreData]);

  const renderMap = (geo) => {
    const el = svgRef.current;
    if (!el) return;

    const width  = el.clientWidth  || 600;
    const height = el.clientHeight || 520;

    const svg = d3.select(el)
      .attr("width", width)
      .attr("height", height);

    svg.selectAll("*").remove(); // clear on re-render

    // Fit map to SVG container
    const projection = d3.geoMercator().fitSize([width, height], geo);
    const path       = d3.geoPath().projection(projection);

    svg
      .append("g")
      .selectAll("path")
      .data(geo.features)
      .join("path")
      .attr("class", "district")
      .attr("d", path)
      .attr("fill", (d) => {
        const raw  = d.properties?.NAME_2 || d.properties?.district || d.properties?.DISTRICT || "";
        const name = resolveDistrict(raw);
        const info = scoreData?.[name];
        return info ? TIER_FILL[info.tier] || DEFAULT_FILL : DEFAULT_FILL;
      })
      .attr("stroke", STROKE)
      .attr("stroke-width", 0.8)
      .style("cursor", "pointer")
      .style("transition", "fill 0.4s ease")
      .on("mouseenter", function (event, d) {
        d3.select(this).attr("stroke", HOVER_STROKE).attr("stroke-width", 2);
        const raw  = d.properties?.NAME_2 || d.properties?.district || d.properties?.DISTRICT || "";
        const name = resolveDistrict(raw);
        if (onDistrictHover) onDistrictHover(name, event.clientX, event.clientY);
      })
      .on("mousemove", function (event, d) {
        const raw  = d.properties?.NAME_2 || d.properties?.district || d.properties?.DISTRICT || "";
        const name = resolveDistrict(raw);
        if (onDistrictHover) onDistrictHover(name, event.clientX, event.clientY);
      })
      .on("mouseleave", function () {
        d3.select(this).attr("stroke", STROKE).attr("stroke-width", 0.8);
        if (onDistrictLeave) onDistrictLeave();
      });

    // District name labels
    svg
      .append("g")
      .selectAll("text")
      .data(geo.features)
      .join("text")
      .attr("transform", (d) => `translate(${path.centroid(d)})`)
      .attr("text-anchor", "middle")
      .attr("dy", "0.3em")
      .attr("font-size", "7px")
      .attr("fill", "rgba(255,255,255,0.6)")
      .attr("pointer-events", "none")
      .text((d) => {
        // Use modern analytics name for labels
        const raw  = d.properties?.NAME_2 || "";
        const name = resolveDistrict(raw);
        return name.length > 10 ? name.slice(0, 9) + "…" : name;
      });
  };

  return (
    <svg
      ref={svgRef}
      style={{ width: "100%", height: "100%", borderRadius: "12px" }}
    />
  );
}
