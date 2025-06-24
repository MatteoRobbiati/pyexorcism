import logging
import itertools

class SimpleExorcism:
    def __init__(self, cubes, verbose=True):
        """
        cubes: list of cube strings, e.g., ['011', '100', '101', '110']
        Each string represents one product term. '-' is a don't care.
        verbose: if True, show info about the minimization process.
        """
        self.cubes = cubes.copy()
        self.initial_cubes = cubes.copy()
        self.initial_cost = len(cubes)
        self.minimized_cost = None

        self.logger = logging.getLogger("SimpleExorcism")
        if verbose:
            self.logger.setLevel(logging.INFO)
        else:
            self.logger.setLevel(logging.WARNING)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(levelname)s][%(name)s] %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def minimize(self):
        changed = True
        iteration = 0
        unlink_done = False
        self.logger.info(f"Starting minimization: {self.initial_cost} cubes")
        while changed:
            changed = False
            new_cubes = []
            skip = set()

            # 1) XOR-cancellation: remove pairs of identical cubes
            counts = {}
            for cube in self.cubes:
                counts[cube] = counts.get(cube, 0) + 1
            before = len(self.cubes)
            self.cubes = [cube for cube, cnt in counts.items() if cnt % 2 == 1]
            after = len(self.cubes)
            if before != after:
                removed = before - after
                self.logger.info(f"Removed {removed} duplicate cubes at iteration {iteration}")
                changed = True

            # 2) Primary x-linking: dist-1 merging & dist-2 splitting
            n = len(self.cubes)
            merges = 0
            splits = 0
            for i in range(n):
                if i in skip: continue
                for j in range(i+1, n):
                    if j in skip: continue
                    dist, diff_positions = self._cube_distance(self.cubes[i], self.cubes[j])
                    if dist == 1:
                        # merge differing bit
                        pos = diff_positions[0]
                        merged = self._merge(self.cubes[i], self.cubes[j], pos)
                        new_cubes.append(merged)
                        skip.update({i, j})
                        merges += 1
                        changed = True
                        break
                    elif dist == 2:
                        # split into two cubes, one per differing position
                        p, q = diff_positions
                        c1, c2 = self.cubes[i], self.cubes[j]
                        # split on first differing pos
                        split1 = c1[:p] + '-' + c1[p+1:]
                        # split on second differing pos
                        split2 = c1[:q] + '-' + c1[q+1:]
                        new_cubes.extend([split1, split2])
                        skip.update({i, j})
                        splits += 1
                        changed = True
                        break
                if changed and (merges + splits) > 0:
                    break

            if merges > 0:
                self.logger.info(f"Merged {merges} pairs at iteration {iteration}")
            if splits > 0:
                self.logger.info(f"Split {splits} pairs at iteration {iteration}")

            # Rebuild cubes: retain unmerged/split, add new
            result = [cube for idx, cube in enumerate(self.cubes) if idx not in skip]
            result.extend(new_cubes)
            self.cubes = result

            # 3) Unlinking: do exactly one split of a '-' cube (ever)
            if not changed and not unlink_done:
                for idx, cube in enumerate(self.cubes):
                    if '-' in cube:
                        pos = cube.index('-')
                        c0 = cube[:pos] + '0' + cube[pos+1:]
                        c1 = cube[:pos] + '1' + cube[pos+1:]
                        self.cubes.pop(idx)
                        self.cubes.extend([c0, c1])
                        self.logger.info(f"Unlinked cube {cube} into {c0}, {c1} at iteration {iteration}")
                        changed = True
                        unlink_done = True
                        break

            iteration += 1

        self.minimized_cost = len(self.cubes)
        reduction = self.initial_cost - self.minimized_cost
        self.logger.info(f"Minimization complete: {self.minimized_cost} cubes remain (reduced by {reduction})")
        return self.cubes

    def _cube_distance(self, c1, c2):
        """Return (number of differing literal positions, list of those positions)."""
        diff = []
        for i, (a, b) in enumerate(zip(c1, c2)):
            if a != b:
                # both are concrete literals 0/1
                if a != '-' and b != '-':
                    diff.append(i)
                else:
                    # incomparable (literal vs '-') for primary linking
                    return (float('inf'), [])
        return (len(diff), diff)

    def _merge(self, c1, c2, pos):
        """Merge two cubes differing at position pos into a don't-care there."""
        return c1[:pos] + '-' + c1[pos+1:]

    @staticmethod
    def from_pla(pla_lines):
        """Parse cubes with output 1 from PLA lines (list of str)"""
        cubes = []
        for line in pla_lines:
            line = line.strip()
            if not line or line.startswith('.'):
                continue
            parts = line.split()
            if len(parts) == 2 and parts[1] == '1':
                cubes.append(parts[0])
        return SimpleExorcism(cubes)

    def evaluate(self, assignment):
        """Evaluate the original ESOP on a single assignment."""
        total = 0
        for cube in self.initial_cubes:
            match = True
            for bit, lit in zip(assignment, cube):
                if lit != '-' and lit != bit:
                    match = False
                    break
            if match:
                total ^= 1
        return total

    def minimized_evaluate(self, assignment):
        """Evaluate the minimized ESOP on a single assignment."""
        total = 0
        for cube in self.cubes:
            match = True
            for bit, lit in zip(assignment, cube):
                if lit != '-' and lit != bit:
                    match = False
                    break
            if match:
                total ^= 1
        return total

    def is_equivalent(self):
        """Check equivalence by brute-force over all assignments."""
        if self.minimized_cost is None:
            raise RuntimeError("Call minimize() first.")
        n = len(self.initial_cubes[0])
        for bits in itertools.product('01', repeat=n):
            if self.evaluate(bits) != self.minimized_evaluate(bits):
                return False
        return True

    def cost_reduction(self):
        """Returns (initial_cost, minimized_cost, ratio)"""
        if self.minimized_cost is None:
            raise RuntimeError("Call minimize() first.")
        ratio = (self.initial_cost / self.minimized_cost
                 if self.minimized_cost else float('inf'))
        return self.initial_cost, self.minimized_cost, ratio
