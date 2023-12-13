const std = @import("std");
const Allocator = std.mem.Allocator;

pub fn main() !void {
    // Prints to stderr (it's a shortcut based on `std.io.getStdErr()`)
    std.debug.print("All your {s} are belong to us.\n", .{"codebase"});

    // stdout is for the actual output of your application, for example if you
    // are implementing gzip, then only the compressed bytes should be sent to
    // stdout, not any debugging messages.
    const stdout_file = std.io.getStdOut().writer();
    var bw = std.io.bufferedWriter(stdout_file);
    const stdout = bw.writer();

    try stdout.print("Run `zig build test` to run the tests.\n", .{});

    try bw.flush(); // don't forget to flush!

    // Reading JSON from https://www.openmymind.net/Reading-A-Json-Config-In-Zig/
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    const allocator = gpa.allocator();

    const parsed = try readInput(allocator, "input.json");
    defer parsed.deinit();

    const input = parsed.value;
    const next_key = input.next_mapping.get("seed").?;
    std.debug.print("input.next_mapping: {}\n", .{next_key});
}

fn readInput(allocator: Allocator, path: []const u8) !std.json.Parsed(Input) {
    const stat = try std.fs.cwd().statFile(path);
    const data = try std.fs.cwd().readFileAlloc(allocator, path, stat.size);
    defer allocator.free(data);
    return std.json.parseFromSlice(Input, allocator, data, .{ .allocate = .alloc_always });
}

const Input = struct {
    next_mapping: *std.StringArrayHashMap([]const u8),
};

test "simple test" {
    var list = std.ArrayList(i32).init(std.testing.allocator);
    defer list.deinit(); // try commenting this out and see if zig detects the memory leak!
    try list.append(42);
    try std.testing.expectEqual(@as(i32, 42), list.pop());
}
