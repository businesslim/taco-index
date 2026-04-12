"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
} from "recharts";
import { IndexHistoryPoint } from "@/lib/api";

interface Props {
  data: IndexHistoryPoint[];
}

export default function IndexHistoryChart({ data }: Props) {
  if (data.length === 0) {
    return (
      <p className="text-gray-500 text-sm">
        No history data yet. Check back after the first few pipeline runs.
      </p>
    );
  }

  const chartData = [...data].reverse().map((point) => {
    const d = new Date(point.calculated_at);
    const date = d.toLocaleDateString("en-US", { month: "short", day: "numeric", timeZone: "UTC" });
    const time = d.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", hour12: false, timeZone: "UTC" });
    return {
      date: `${date} ${time}`,
      value: point.index_value,
      label: point.band_label,
      fullTime: d.toLocaleString("en-US", { timeZone: "UTC", timeZoneName: "short" }),
    };
  });

  return (
    <ResponsiveContainer width="100%" height={200}>
      <LineChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
        <XAxis
          dataKey="date"
          tick={{ fill: "#9CA3AF", fontSize: 11 }}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          domain={[0, 100]}
          tick={{ fill: "#9CA3AF", fontSize: 11 }}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: "#1F2937",
            border: "1px solid #374151",
            borderRadius: 8,
          }}
          labelStyle={{ color: "#D1D5DB" }}
          itemStyle={{ color: "#F9FAFB" }}
          formatter={(value) => [value, "TACO Index"]}
        />
        <ReferenceLine y={50} stroke="#6B7280" strokeDasharray="4 4" />
        <Line
          type="monotone"
          dataKey="value"
          stroke="#32CD32"
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 4, fill: "#32CD32" }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
