
def tupel(i, j):
	 return (i + 1, j + 1)

ALL_CELLS = [(i, j) for j in range(9) for i in range(9)]

ALL_TUPLES = [([(i, j) for j in range(9)], 'row {}'.format(i + 1)) for i in range(9)]
ALL_TUPLES += [([(i, j) for i in range(9)], 'col {}'.format(j + 1)) for j in range(9)]
ALL_TUPLES += [([(i, j) for i in range(k, k + 3) for j in range(l, l + 3)], 'square {}'.format(tupel(k // 3 , l // 3))) for k in range(0, 9, 3) for l in range(0, 9, 3)]

def _nearby_cells(i, j):
	def same_sq(x):
		return[[x+1, x+2], [x-1, x+1], [x-2, x-1]][x % 3]
	result = [(k, j) for k in range(9) if not k == i]
	result += [(i, l) for l in range(9) if not l == j]
	result += [(k, l) for k in same_sq(i) for l in same_sq(j)]
	return result
NEARBY_CELLS = [[_nearby_cells(i, j) for j in range(9)] for i in range(9)]

def parse_sdk(ascii_lines):
	sudoku = []
	for line in ascii_lines:
		line = (line + ' ' * (9 - len(line)))[:9]
		sudoku.append([(int(i) if i.isdigit() else None) for i in line])
		if len(sudoku) == 9:
			break
	while len(sudoku) < 9:
		sudoku += [[None] * 9]
	return sudoku

def print_sdk(sudoku, log = print):
	def pchr(i, j):
		value = sudoku[i][j]
		return str(value) if value else ' '
	log("/" + "-" * 23 + "\\")
	for i in range(9):
		line = " | ".join([ " ".join([pchr(i, 3*j + k) for k in range(3)]) for j in range(3)])
		log("| " + line + " |")
		if i in [2, 5]:
			log("|" + "-" * 23 + "|")
	log("\\" + "-" * 23 + "/")

def copy_sdk(sudoku):
	return [[sudoku[i][j] for j in range(9)] for i in range(9)]
	
def get_free_cells(sudoku):
	return [(i, j) for j in range(9) for i in range(9) if not sudoku[i][j]]

def get_filled_values(sudoku, cells):
	return [sudoku[i][j] for (i, j) in cells if sudoku[i][j]]

def get_candidates(sudoku, cells):
	filled_values = get_filled_values(sudoku, cells)
	return [value for value in range(1, 10) if not value in filled_values]

def find_candidates(sudoku):
	candidates_map = [[[] for j in range(9)] for i in range(9)]
	for (i, j) in get_free_cells(sudoku):
		candidates_map[i][j] = get_candidates(sudoku, NEARBY_CELLS[i][j])
	return candidates_map

def check_duplicates(sudoku, candidates_map):
	for (cells, name) in ALL_TUPLES:
		filled_values = get_filled_values(sudoku, cells)
		dupes = [value for (i, value) in enumerate(filled_values) if not filled_values.index(value) == i]
		if dupes:
			return None, 'Duplicate {} in {}'.format(dupes[0], name)
	return [], None

def find_single_candidates(sudoku, candidates_map):
	result = []
	for (i, j) in get_free_cells(sudoku):
		candidates = candidates_map[i][j]
		if len(candidates) == 1:
			result.append(((i, j), candidates[0], "only allowed value"))
		if len(candidates) == 0:
			return None, 'No value allowed for {}'.format(tupel(i, j))
	return result, None

def find_single_allowed_cells(sudoku, candidates_map):
	result = []
	for (cells, name) in ALL_TUPLES:
		for value in get_candidates(sudoku, cells):
			allowed_cells = [(i, j) for (i, j) in cells if value in candidates_map[i][j]]
			if len(allowed_cells) == 1:
				result.append((allowed_cells[0], value, 'only allowed cell within {}'.format(name)))
			if len(allowed_cells) == 0:
				return None, 'Value {} not allowed in {}'.format(value, name)
	return result, None

ALGORITHMS = [check_duplicates, find_single_candidates, find_single_allowed_cells]
def apply_algorithms(sudoku):
	candidates_map = find_candidates(sudoku)
	result = []
	for algorithm in ALGORITHMS:
		new_values, inconsistency = algorithm(sudoku, candidates_map)
		if inconsistency:
			return None, inconsistency
		for value in new_values:
			if not value[0] in [v[0] for v in result]:
				result.append(value)
	return result, None

def set_new_values(sudoku, new_values, log):
	for ((i, j), value, reason) in new_values:
		log('Insert {} into {} because {}'.format(value, tupel(i, j), reason))
		sudoku[i][j] = value

def shallow_exclude(sudoku, max_step_count):
	step_count = 0
	while True:
		new_values, inconsistency = apply_algorithms(sudoku)
		if inconsistency:
			return True, step_count
		if new_values:
			step_count += len(new_values)
			if step_count > max_step_count:
				return False, 0
			set_new_values(sudoku, new_values, lambda text: None)
		else:
			return False, 0

def shallow_guess_binary_options(sudoku):
	candidates_map = find_candidates(sudoku)
	options = [(i, j) for (i, j) in get_free_cells(sudoku) if len(candidates_map[i][j]) == 2]
	min_step_count = 81
	result = None
	for (i, j) in options:
		[value_1, value_2] = candidates_map[i][j]
		copy = copy_sdk(sudoku)
		copy[i][j] = value_1
		excluded, step_count = shallow_exclude(copy, min_step_count)
		if excluded:
			min_step_count = step_count
			result = (value_1, value_2, (i, j))
		copy = copy_sdk(sudoku)
		copy[i][j] = value_2
		excluded, step_count = shallow_exclude(copy, min_step_count)
		if excluded:
			min_step_count = step_count
			result = (value_2, value_1, (i, j))
	return result
	
def find_least_candidates(sudoku):
	candidates_map = find_candidates(sudoku)
	min = None
	min_len = 9
	for (i, j) in get_free_cells(sudoku):
		candidates = candidates_map[i][j]
		length = len(candidates)
		if length > 1 and length < min_len:
			min = ((i, j), candidates)
			min_len = length
	return min
	
def solve(original_sudoku, log_fn, max_solutions = 1, binary_assume = True, guess_recursive = True, depth = 0):
	def log(text):
		log_fn(text, depth)
	
	sudoku = copy_sdk(original_sudoku)
	while True:
		print_sdk(sudoku, log)

		new_values, inconsistency = apply_algorithms(sudoku)
		if inconsistency:
			log(inconsistency)
			return []
		if new_values:
			set_new_values(sudoku, new_values, log)
			continue
		if not binary_assume:
			break
		guess_result = shallow_guess_binary_options(sudoku)
		if guess_result:
			exclude_value, value, (i, j) = guess_result
			log('Assuming {} for {} leads to'.format(exclude_value, tupel(i, j)))
			sudoku[i][j] = exclude_value
			solve(sudoku, log_fn, depth = depth + 1)
			log('Hence inserting {} for {}'.format(value, tupel(i, j)))
			sudoku[i][j] = value
		else:
			break

	least_candidates = find_least_candidates(sudoku)
	if not least_candidates:
		log('!  ' * 9 + 'Solved' + '  !' * 9)
		return [sudoku]
	
	solutions = []
	if guess_recursive:
		(i, j), candidates = least_candidates
		log('Guessing values for {} from {}'.format(tupel(i, j), candidates))
		for value in candidates:
			sudoku[i][j] = value
			log('Guessing value {} for {}'.format(value, tupel(i, j)))
			new_solutions = solve(sudoku, log_fn, max_solutions - len(solutions), binary_assume, True, depth + 1)
			if new_solutions:
				solutions += new_solutions
				if len(solutions) >= max_solutions:
					break
			else:
				log('Guess {} failed for {}'.format(value, tupel(i, j)))
	return solutions

def print_log_fn(text, depth):
	print('  ' * depth + text)

def main():
	from sys import stdin
	sudoku = parse_sdk(stdin)
	solutions = solve(sudoku, print_log_fn)
	print('Solution count: {}'.format(len(solutions)))

if __name__ == "__main__":
	main()
