# -*- coding: utf-8 -*-
import re

import pytest
import numpy as np
import pandas as pd
import pandas.util.testing as tm

import bulwark.checks as ck
import bulwark.decorators as dc


def _add_n(df, n=1):
    return df + n


def _noop(df):
    return df


@pytest.mark.parametrize("df,columns,exact_cols,exact_order",
                         [(pd.DataFrame({"a": [1], "b": [2], "c": [3]}), ["a", "b", "c"], True, True),
                          (pd.DataFrame({"a": [1], "b": [2], "c": [3]}), ["a", "b"], False, False),
                          (pd.DataFrame({"a": [1], "b": [2], "c": [3]}), ["a", "b"], False, True),
                          (pd.DataFrame({"a": [1], "b": [2], "c": [3]}), ["b", "c"], False, True),
                          pytest.param(pd.DataFrame({"a": [1], "b": [2], "c": [3]}),
                                       ["a", "b"], True, True, marks=pytest.mark.xfail),
                          pytest.param(pd.DataFrame({"a": [1], "b": [2], "c": [3]}),
                                       ["b", "a"], False, True, marks=pytest.mark.xfail),
                          pytest.param(pd.DataFrame({"a": [1], "b": [2], "c": [3]}),
                                       ["w", "b", "a"], False, True, marks=pytest.mark.xfail)]
                         )
def test_has_columns(df, columns, exact_cols, exact_order):
    ck.has_columns(df, columns, exact_cols, exact_order)


def test_is_shape():
    shape = 10, 2
    ig_0 = -1, 2
    ig_1 = 10, -1
    ig_2 = None, 2
    ig_3 = 10, None
    shapes = [shape, ig_0, ig_1, ig_2, ig_3]
    df = pd.DataFrame(np.random.randn(*shape))
    for shp in shapes:
        tm.assert_frame_equal(df, ck.is_shape(df, shp))
    for shp in shapes:
        result = dc.IsShape(shape=shp)(_add_n)(df, 2)
        tm.assert_frame_equal(result, df + 2)

        result = dc.IsShape(shape=shp)(_noop)(df)
        tm.assert_frame_equal(result, df)

        result = dc.IsShape(shp)(_add_n)(df, 3)  # *arg test
        tm.assert_frame_equal(result, df + 3)

        result = dc.IsShape(shp, enabled=False)(_add_n)(df, 4)  # enabled test
        tm.assert_frame_equal(result, df + 4)

    with pytest.raises(AssertionError):
        ck.is_shape(df, (9, 2))
        dc.IsShape((9, 2))(_add_n)(df)
    with pytest.raises(TypeError):
        dc.IsShape(shape=(9, 2), cheese=True)(_add_n)(df)  # bad dc param check


def test_has_no_x():
    df = pd.DataFrame([1, 2, 3], index=['a', 'b', 'c'])
    result = ck.has_no_x(df, values=['x', 'y', 'z'])
    tm.assert_frame_equal(df, result)

    result = dc.HasNoX()(_add_n)(df, 2)
    tm.assert_frame_equal(result, df + 2)
    result = dc.HasNoX()(_add_n)(df, n=2)
    tm.assert_frame_equal(result, df + 2)


def test_has_no_nans():
    df = pd.DataFrame(np.random.randn(5, 3))
    result = ck.has_no_nans(df)
    tm.assert_frame_equal(df, result)

    result = dc.HasNoNans()(_add_n)(df, 2)
    tm.assert_frame_equal(result, df + 2)
    result = dc.HasNoNans()(_add_n)(df, n=2)
    tm.assert_frame_equal(result, df + 2)


def test_has_no_nones():
    df = pd.DataFrame(np.random.randn(5, 3))
    result = ck.has_no_nones(df)
    tm.assert_frame_equal(df, result)

    result = dc.HasNoNones()(_add_n)(df, 2)
    tm.assert_frame_equal(result, df + 2)
    result = dc.HasNoNones()(_add_n)(df, n=2)
    tm.assert_frame_equal(result, df + 2)


def test_has_no_infs():
    df = pd.DataFrame(np.random.randn(5, 3))
    result = ck.has_no_infs(df)
    tm.assert_frame_equal(df, result)

    result = dc.HasNoInfs()(_add_n)(df, 2)
    tm.assert_frame_equal(result, df + 2)
    result = dc.HasNoInfs()(_add_n)(df, n=2)
    tm.assert_frame_equal(result, df + 2)


def test_has_no_neg_infs():
    df = pd.DataFrame(np.random.randn(5, 3))
    result = ck.has_no_neg_infs(df)
    tm.assert_frame_equal(df, result)

    result = dc.HasNoNegInfs()(_add_n)(df, 2)
    tm.assert_frame_equal(result, df + 2)
    result = dc.HasNoNegInfs()(_add_n)(df, n=2)
    tm.assert_frame_equal(result, df + 2)


def test_has_no_nans_raises():
    df = pd.DataFrame(np.random.randn(5, 3))
    df.iloc[0, 0] = np.nan
    with pytest.raises(AssertionError):
        ck.has_no_nans(df)

    with pytest.raises(AssertionError):
        dc.HasNoNans()(_add_n)(df, n=2)


def test_has_set_within_vals():
    df = pd.DataFrame({'A': [1, 2, 3], 'B': ['a', 'b', 'c']})

    items = {'A': [1, 2, 3], 'B': ['a', 'b', 'c']}
    tm.assert_frame_equal(df, ck.has_set_within_vals(df, items))
    tm.assert_frame_equal(df, dc.HasSetWithinVals(items=items)(_noop)(df))

    items = {'A': [1, 2], 'B': ['a', 'b']}
    tm.assert_frame_equal(df, ck.has_set_within_vals(df, items))
    tm.assert_frame_equal(df, dc.HasSetWithinVals(items=items)(_noop)(df))

    items = {'A': [1, 2, 4], 'B': ['a', 'b', 'd']}
    with pytest.raises(AssertionError):
        ck.has_set_within_vals(df, items)
    with pytest.raises(AssertionError):
        dc.HasSetWithinVals(items=items)(_noop)(df)


def test_unique():
    df = pd.DataFrame([[1, 2, 3], ['a', 'b', 'c']])
    tm.assert_frame_equal(df, ck.unique(df))
    result = dc.Unique()(_noop)(df)
    tm.assert_frame_equal(result, df)

    df = pd.DataFrame([[1, 2, 3], [1, 'b', 'c']])
    with pytest.raises(AssertionError):
        ck.unique(df)
    with pytest.raises(AssertionError):
        dc.Unique()(_noop)(df)


def test_unique_index():
    df = pd.DataFrame([1, 2, 3], index=['a', 'b', 'c'])
    tm.assert_frame_equal(df, ck.has_unique_index(df))
    result = dc.HasUniqueIndex()(_add_n)(df)
    tm.assert_frame_equal(result, df + 1)

    with pytest.raises(AssertionError):
        ck.has_unique_index(df.reindex(['a', 'a', 'b']))
    with pytest.raises(AssertionError):
        dc.HasUniqueIndex()(_add_n)(df.reindex(['a', 'a', 'b']))


def test_monotonic_increasing_lax():
    df = pd.DataFrame([1, 2, 2])
    tm.assert_frame_equal(df, ck.is_monotonic(df, increasing=True))
    result = dc.IsMonotonic(increasing=True)(_add_n)(df)
    tm.assert_frame_equal(result, df + 1)

    df = pd.DataFrame([1, 2, 1])
    with pytest.raises(AssertionError):
        ck.is_monotonic(df, increasing=True)
    with pytest.raises(AssertionError):
        dc.IsMonotonic(increasing=True)(_add_n)(df)

    df = pd.DataFrame([3, 2, 1])
    with pytest.raises(AssertionError):
        ck.is_monotonic(df, increasing=True)
    with pytest.raises(AssertionError):
        dc.IsMonotonic(increasing=True)(_add_n)(df)


def test_monotonic_increasing_strict():
    df = pd.DataFrame([1, 2, 3])
    tm.assert_frame_equal(df, ck.is_monotonic(df, increasing=True, strict=True))
    result = dc.IsMonotonic(increasing=True, strict=True)(_add_n)(df)
    tm.assert_frame_equal(result, df + 1)

    df = pd.DataFrame([1, 2, 2])
    with pytest.raises(AssertionError):
        ck.is_monotonic(df, increasing=True, strict=True)
    with pytest.raises(AssertionError):
        dc.IsMonotonic(increasing=True, strict=True)(_add_n)(df)

    df = pd.DataFrame([3, 2, 1])
    with pytest.raises(AssertionError):
        ck.is_monotonic(df, increasing=True, strict=True)
    with pytest.raises(AssertionError):
        dc.IsMonotonic(increasing=True, strict=True)(_add_n)(df)


def test_monotonic_decreasing():
    df = pd.DataFrame([2, 2, 1])
    tm.assert_frame_equal(df, ck.is_monotonic(df, increasing=False))
    result = dc.IsMonotonic(increasing=False)(_add_n)(df)
    tm.assert_frame_equal(result, df + 1)

    df = pd.DataFrame([1, 2, 1])
    with pytest.raises(AssertionError):
        ck.is_monotonic(df, increasing=False)
    with pytest.raises(AssertionError):
        dc.IsMonotonic(increasing=False)(_add_n)(df)

    df = pd.DataFrame([1, 2, 3])
    with pytest.raises(AssertionError):
        ck.is_monotonic(df, increasing=False)
    with pytest.raises(AssertionError):
        dc.IsMonotonic(increasing=False)(_add_n)(df)


def test_monotonic_decreasing_strict():
    df = pd.DataFrame([3, 2, 1])
    tm.assert_frame_equal(df, ck.is_monotonic(df, increasing=False,
                                              strict=True))
    result = dc.IsMonotonic(increasing=False, strict=True)(_add_n)(df)
    tm.assert_frame_equal(result, df + 1)

    df = pd.DataFrame([2, 2, 1])
    with pytest.raises(AssertionError):
        ck.is_monotonic(df, increasing=False, strict=True)
    with pytest.raises(AssertionError):
        dc.IsMonotonic(increasing=False, strict=True)(_add_n)(df)

    df = pd.DataFrame([1, 2, 3])
    with pytest.raises(AssertionError):
        ck.is_monotonic(df, increasing=False, strict=True)
    with pytest.raises(AssertionError):
        dc.IsMonotonic(increasing=False, strict=True)(_add_n)(df)


def test_monotonic_either():
    df = pd.DataFrame({'A': [1, 2, 2], 'B': [3, 2, 2]})
    tm.assert_frame_equal(df, ck.is_monotonic(df))
    result = dc.IsMonotonic()(_add_n)(df)
    tm.assert_frame_equal(result, df + 1)

    df = pd.DataFrame({'A': [1, 2, 3], 'B': [1, 2, 1]})
    with pytest.raises(AssertionError):
        ck.is_monotonic(df)
    with pytest.raises(AssertionError):
        dc.IsMonotonic()(_add_n)(df)


def test_monotonic_either_stict():
    df = pd.DataFrame({'A': [1, 2, 3], 'B': [3, 2, 1]})
    tm.assert_frame_equal(df, ck.is_monotonic(df, strict=True))
    result = dc.IsMonotonic(strict=True)(_add_n)(df)
    tm.assert_frame_equal(result, df + 1)

    df = pd.DataFrame({'A': [1, 2, 2], 'B': [3, 2, 2]})
    with pytest.raises(AssertionError):
        ck.is_monotonic(df, strict=True)
    with pytest.raises(AssertionError):
        dc.IsMonotonic(strict=True)(_add_n)(df)


def test_monotonic_items():
    df = pd.DataFrame({'A': [1, 2, 3], 'B': [3, 2, 3]})
    tm.assert_frame_equal(df, ck.is_monotonic(df, items={'A': (True, True)}))
    tm.assert_frame_equal(dc.IsMonotonic(items={'A': (True, True)}, strict=True)(_add_n)(
        df), df + 1)


def test_within_set():
    df = pd.DataFrame({'A': [1, 2, 3], 'B': ['a', 'b', 'c']})
    items = {'A': [1, 2, 3], 'B': ['a', 'b', 'c']}
    tm.assert_frame_equal(df, ck.within_set(df, items))
    tm.assert_frame_equal(df, dc.WithinSet(items=items)(_noop)(df))

    items.pop('A')
    tm.assert_frame_equal(df, ck.within_set(df, items))
    tm.assert_frame_equal(df, dc.WithinSet(items=items)(_noop)(df))

    items['A'] = [1, 2]
    with pytest.raises(AssertionError):
        ck.within_set(df, items)
    with pytest.raises(AssertionError):
        dc.WithinSet(items=items)(_noop)(df)


def test_within_range():
    df = pd.DataFrame({'A': [-1, 0, 1]})
    items = {'A': (-1, 1)}
    tm.assert_frame_equal(df, ck.within_range(df, items))
    tm.assert_frame_equal(df, dc.WithinRange(items)(_noop)(df))

    items['A'] = (0, 1)
    with pytest.raises(AssertionError):
        ck.within_range(df, items)
    with pytest.raises(AssertionError):
        dc.WithinRange(items)(_noop)(df)


def test_within_n_std():
    df = pd.DataFrame({'A': np.arange(10), 'B': list('abcde') * 2})
    tm.assert_frame_equal(df, ck.within_n_std(df))
    tm.assert_frame_equal(df, dc.WithinNStd()(_noop)(df))

    with pytest.raises(AssertionError):
        ck.within_n_std(df, .5)
    with pytest.raises(AssertionError):
        dc.WithinNStd(.5)(_noop)(df)


def test_has_dtypes():
    df = pd.DataFrame({'A': np.random.randint(0, 10, 10),
                       'B': np.random.randn(10),
                       'C': list('abcdefghij'),
                       'D': pd.Categorical(np.random.choice(['a', 'b'], 10))})
    dtypes = {'A': int, 'B': 'float', 'C': object, 'D': 'category'}
    tm.assert_frame_equal(df, ck.has_dtypes(df, dtypes))
    tm.assert_frame_equal(df, dc.HasDtypes(items=dtypes)(_noop)(df))

    with pytest.raises(AssertionError):
        ck.has_dtypes(df, {'A': float})

    with pytest.raises(AssertionError):
        dc.HasDtypes(items={'A': bool})(_noop)(df)


def test_one_to_many():
    df = pd.DataFrame({
        'parameter': ['Cu', 'Cu', 'Pb', 'Pb'],
        'units': ['ug/L', 'ug/L', 'ug/L', 'ug/L'],
        'res': [2.0, 4.0, 6.0, 8.0]
    })
    result = ck.one_to_many(df, 'units', 'parameter')
    tm.assert_frame_equal(df, result)


def test_one_to_many_raises():
    df = pd.DataFrame({
        'parameter': ['Cu', 'Cu', 'Pb', 'Pb'],
        'units': ['ug/L', 'ug/L', 'ug/L', 'mg/L'],
        'res': [2.0, 4.0, 6.0, 0.008]
    })
    with pytest.raises(AssertionError):
        ck.one_to_many(df, 'units', 'parameter')


def test_is_same_as():
    df = pd.DataFrame({'A': [1, 2, 3], 'B': [1, 2, 3]})
    df_equal = pd.DataFrame({'A': [1, 2, 3], 'B': [1, 2, 3]})
    df_not_equal = pd.DataFrame({'A': [1, 2, 3], 'B': [1, 2, 1]})

    result = ck.is_same_as(df, df_equal)
    tm.assert_frame_equal(df, result)

    result = dc.IsSameAs(df_equal)(_noop)(df)
    tm.assert_frame_equal(df, result)

    with pytest.raises(AssertionError):
        ck.is_same_as(df, df_not_equal)
        dc.IsSameAs(df_not_equal)(_noop)(df)


def test_is_same_as_with_kwargs():
    df = pd.DataFrame({'A': [1, 2, 3], 'B': [1, 2, 3]})
    df_equal = pd.DataFrame({'A': [1, 2, 3], 'B': [1, 2, 3]})
    df_equal_float = pd.DataFrame({'A': [1.0, 2, 3], 'B': [1, 2, 3.0]})

    result = ck.is_same_as(df, df_equal, check_dtype=True)
    tm.assert_frame_equal(df, result)

    result = dc.IsSameAs(df_equal, check_dtype=True)(_noop)(df)
    tm.assert_frame_equal(df, result)

    with pytest.raises(AssertionError):
        ck.is_same_as(df, df_equal_float, check_dtype=True)
        dc.IsSameAs(df_equal_float, check_dtype=True)(_noop)(df)

    result = ck.is_same_as(df, df_equal_float, check_dtype=False)
    tm.assert_frame_equal(df, result)

    result = dc.IsSameAs(df_equal_float, check_dtype=False)(_noop)(df)  # todo see why this fails
    tm.assert_frame_equal(df, result)


def test_matches_regex():
    df = pd.DataFrame({'A': ['aa', 'ab', 'ac'], 'B': ['ad', 'ae', 'a1']})
    pattern = r'a.'
    result = ck.matches_regex(df, pattern)
    tm.assert_frame_equal(df, result)

    result = dc.MatchesRegex(pattern)(_noop)(df)
    tm.assert_frame_equal(df, result)

    pattern = r'aa'
    with pytest.raises(AssertionError):
        ck.matches_regex(df, pattern)
        dc.MatchesRegex(pattern)(_noop)(df)


def test_matches_regex_with_columns():
    df = pd.DataFrame({'A': ['aa', 'ab', 'ac'], 'B': ['ad', 'ae', 'a1']})
    pattern = r'a.'
    result = ck.matches_regex(df, pattern, columns=['A'])
    tm.assert_frame_equal(df, result)

    result = dc.MatchesRegex(pattern, columns=['A'])(_noop)(df)
    tm.assert_frame_equal(df, result)

    pattern = r'a[a-z]'
    with pytest.raises(AssertionError):
        ck.matches_regex(df, pattern, columns=['B'])
        dc.MatchesRegex(pattern, columns=['B'])(_noop)(df)


def test_matches_regex_with_kwargs():
    df = pd.DataFrame({'A': ['aa', 'ab', 'ac'], 'B': ['ad', 'ae', 'a1']})
    pattern = 'A.'
    result = ck.matches_regex(df, pattern, case=False)
    tm.assert_frame_equal(df, result)

    result = dc.MatchesRegex(pattern, case=False)(_noop)(df)
    tm.assert_frame_equal(df, result)

    pattern = 'A.'
    result = ck.matches_regex(df, pattern, flags=re.IGNORECASE)
    tm.assert_frame_equal(df, result)

    result = dc.MatchesRegex(pattern, flags=re.IGNORECASE)(_noop)(df)
    tm.assert_frame_equal(df, result)

    df = pd.DataFrame({'A': ['aa', 'ab', np.nan]})
    pattern = 'a.'

    # should raise because of the nan
    with pytest.raises(AssertionError):
        ck.matches_regex(df, pattern)
        dc.MatchesRegex(pattern)(_noop)(df)

    result = ck.matches_regex(df, pattern, na='az')
    tm.assert_frame_equal(df, result)

    result = dc.MatchesRegex(pattern, na='az')(_noop)(df)
    tm.assert_frame_equal(df, result)


def test_multi_check():
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    result = ck.multi_check(df,
                            checks={ck.has_no_nans: {"columns": None},
                                    ck.is_shape: {"shape": (3, 2)}},
                            warn=False)
    tm.assert_frame_equal(df, result)

    result = dc.MultiCheck(checks={ck.has_no_nans: {"columns": None},
                                   ck.is_shape: {"shape": (3, 2)}},
                           warn=False)(_noop)(df)
    tm.assert_frame_equal(df, result)

    def total_sum_not_equal(df, amt):
        if amt == 51:
            raise AssertionError("Test")
        return True

    result = ck.multi_check(df,
                            checks={ck.has_no_nans: {"columns": None},
                                    total_sum_not_equal: {"amt": 52}},
                            warn=False)
    tm.assert_frame_equal(df, result)

    result = dc.MultiCheck(checks={ck.has_no_nans: {"columns": None},
                                   total_sum_not_equal: {"amt": 52}},
                           warn=False)(_noop)(df)
    tm.assert_frame_equal(df, result)

    with pytest.raises(AssertionError):
        result = dc.MultiCheck(checks={ck.has_no_nans: {"columns": None},
                                       total_sum_not_equal: {"amt": 51}},
                               warn=False)(_noop)(df)

    # with pytest.raises(AssertionError):


def test_custom_check():
    def f(df, length):
        if len(df) <= length:
            raise AssertionError("df is not as long as expected.")  # must raise assertionerror
        return df

    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})

    tm.assert_frame_equal(df, ck.custom_check(f, df=df, length=2))
    tm.assert_frame_equal(df, ck.custom_check(f, df, 2))

    # order is verify_func, verif_kwargs, decorated_func
    tm.assert_frame_equal(df, dc.CustomCheck(f, length=2)(_noop)(df))
    tm.assert_frame_equal(df, dc.CustomCheck(f, 2)(_noop)(df))

    with pytest.raises(AssertionError):
        ck.custom_check(f, df=df, length=4)

    with pytest.raises(AssertionError):
        dc.CustomCheck(f, 4)(_noop)(df)
