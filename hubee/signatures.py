signatures = list()

# AggregateFeatureCollection.array
# Aggregates over a given property of the objects in a collection,
# calculating a list of all the values of the selected property.
#
# Args:
#   collection: The collection to aggregate over.
#   property: The property to use from each element of the
#       collection.
signatures.append({'args': [{'description': 'The collection to aggregate over.', 'name': 'collection', 'type': 'FeatureCollection'}, {'description': 'The property to use from each element of the collection.', 'name': 'property', 'type': 'String'}], 'description': 'Aggregates over a given property of the objects in a collection, calculating a list of all the values of the selected property.', 'returns': 'Object', 'type': 'Algorithm', 'hidden': False, 'name': 'AggregateFeatureCollection.array'})
# AggregateFeatureCollection.count
# Aggregates over a given property of the objects in a collection,
# calculating the number of non-null values of the property.
#
# Args:
#   collection: The collection to aggregate over.
#   property: The property to use from each element of the
#       collection.
signatures.append({'args': [{'description': 'The collection to aggregate over.', 'name': 'collection', 'type': 'FeatureCollection'}, {'description': 'The property to use from each element of the collection.', 'name': 'property', 'type': 'String'}], 'description': 'Aggregates over a given property of the objects in a collection, calculating the number of non-null values of the property.', 'returns': 'Object', 'type': 'Algorithm', 'hidden': False, 'name': 'AggregateFeatureCollection.count'})
# AggregateFeatureCollection.count_distinct
# Aggregates over a given property of the objects in a collection,
# calculating the number of distinct values for the selected property.
#
# Args:
#   collection: The collection to aggregate over.
#   property: The property to use from each element of the
#       collection.
signatures.append({'args': [{'description': 'The collection to aggregate over.', 'name': 'collection', 'type': 'FeatureCollection'}, {'description': 'The property to use from each element of the collection.', 'name': 'property', 'type': 'String'}], 'description': 'Aggregates over a given property of the objects in a collection, calculating the number of distinct values for the selected property.', 'returns': 'Object', 'type': 'Algorithm', 'hidden': False, 'name': 'AggregateFeatureCollection.count_distinct'})
# AggregateFeatureCollection.first
# Aggregates over a given property of the objects in a collection,
# calculating the property value of the first object in the collection.
#
# Args:
#   collection: The collection to aggregate over.
#   property: The property to use from each element of the
#       collection.
signatures.append({'args': [{'description': 'The collection to aggregate over.', 'name': 'collection', 'type': 'FeatureCollection'}, {'description': 'The property to use from each element of the collection.', 'name': 'property', 'type': 'String'}], 'description': 'Aggregates over a given property of the objects in a collection, calculating the property value of the first object in the collection.', 'returns': 'Object', 'type': 'Algorithm', 'hidden': False, 'name': 'AggregateFeatureCollection.first'})
# AggregateFeatureCollection.histogram
# Aggregates over a given property of the objects in a collection,
# calculating a histogram of the selected property.
#
# Args:
#   collection: The collection to aggregate over.
#   property: The property to use from each element of the
#       collection.
signatures.append({'args': [{'description': 'The collection to aggregate over.', 'name': 'collection', 'type': 'FeatureCollection'}, {'description': 'The property to use from each element of the collection.', 'name': 'property', 'type': 'String'}], 'description': 'Aggregates over a given property of the objects in a collection, calculating a histogram of the selected property.', 'returns': 'Object', 'type': 'Algorithm', 'hidden': False, 'name': 'AggregateFeatureCollection.histogram'})
# AggregateFeatureCollection.max
# Aggregates over a given property of the objects in a collection,
# calculating the maximum of the values of the selected property.
#
# Args:
#   collection: The collection to aggregate over.
#   property: The property to use from each element of the
#       collection.
signatures.append({'args': [{'description': 'The collection to aggregate over.', 'name': 'collection', 'type': 'FeatureCollection'}, {'description': 'The property to use from each element of the collection.', 'name': 'property', 'type': 'String'}], 'description': 'Aggregates over a given property of the objects in a collection, calculating the maximum of the values of the selected property.', 'returns': 'Object', 'type': 'Algorithm', 'hidden': False, 'name': 'AggregateFeatureCollection.max'})
# AggregateFeatureCollection.mean
# Aggregates over a given property of the objects in a collection,
# calculating the mean of the selected property.
#
# Args:
#   collection: The collection to aggregate over.
#   property: The property to use from each element of the
#       collection.
signatures.append({'args': [{'description': 'The collection to aggregate over.', 'name': 'collection', 'type': 'FeatureCollection'}, {'description': 'The property to use from each element of the collection.', 'name': 'property', 'type': 'String'}], 'description': 'Aggregates over a given property of the objects in a collection, calculating the mean of the selected property.', 'returns': 'Object', 'type': 'Algorithm', 'hidden': False, 'name': 'AggregateFeatureCollection.mean'})
# AggregateFeatureCollection.min
# Aggregates over a given property of the objects in a collection,
# calculating the minimum of the values of the selected property.
#
# Args:
#   collection: The collection to aggregate over.
#   property: The property to use from each element of the
#       collection.
signatures.append({'args': [{'description': 'The collection to aggregate over.', 'name': 'collection', 'type': 'FeatureCollection'}, {'description': 'The property to use from each element of the collection.', 'name': 'property', 'type': 'String'}], 'description': 'Aggregates over a given property of the objects in a collection, calculating the minimum of the values of the selected property.', 'returns': 'Object', 'type': 'Algorithm', 'hidden': False, 'name': 'AggregateFeatureCollection.min'})
# AggregateFeatureCollection.product
# Aggregates over a given property of the objects in a collection,
# calculating the product of the values of the selected property.
#
# Args:
#   collection: The collection to aggregate over.
#   property: The property to use from each element of the
#       collection.
signatures.append({'args': [{'description': 'The collection to aggregate over.', 'name': 'collection', 'type': 'FeatureCollection'}, {'description': 'The property to use from each element of the collection.', 'name': 'property', 'type': 'String'}], 'description': 'Aggregates over a given property of the objects in a collection, calculating the product of the values of the selected property.', 'returns': 'Object', 'type': 'Algorithm', 'hidden': False, 'name': 'AggregateFeatureCollection.product'})
# AggregateFeatureCollection.sample_sd
# Aggregates over a given property of the objects in a collection,
# calculating the sample std. deviation of the values of the selected
# property.
#
# Args:
#   collection: The collection to aggregate over.
#   property: The property to use from each element of the
#       collection.
signatures.append({'args': [{'description': 'The collection to aggregate over.', 'name': 'collection', 'type': 'FeatureCollection'}, {'description': 'The property to use from each element of the collection.', 'name': 'property', 'type': 'String'}], 'description': 'Aggregates over a given property of the objects in a collection, calculating the sample std. deviation of the values of the selected property.', 'returns': 'Object', 'type': 'Algorithm', 'hidden': False, 'name': 'AggregateFeatureCollection.sample_sd'})
# AggregateFeatureCollection.sample_var
# Aggregates over a given property of the objects in a collection,
# calculating the sample variance of the values of the selected property.
#
# Args:
#   collection: The collection to aggregate over.
#   property: The property to use from each element of the
#       collection.
signatures.append({'args': [{'description': 'The collection to aggregate over.', 'name': 'collection', 'type': 'FeatureCollection'}, {'description': 'The property to use from each element of the collection.', 'name': 'property', 'type': 'String'}], 'description': 'Aggregates over a given property of the objects in a collection, calculating the sample variance of the values of the selected property.', 'returns': 'Object', 'type': 'Algorithm', 'hidden': False, 'name': 'AggregateFeatureCollection.sample_var'})
# AggregateFeatureCollection.stats
# Aggregates over a given property of the objects in a collection,
# calculating the sum, min, max, mean, sample standard deviation, sample
# variance, total standard deviation and total variance of the selected
# property.
#
# Args:
#   collection: The collection to aggregate over.
#   property: The property to use from each element of the
#       collection.
signatures.append({'args': [{'description': 'The collection to aggregate over.', 'name': 'collection', 'type': 'FeatureCollection'}, {'description': 'The property to use from each element of the collection.', 'name': 'property', 'type': 'String'}], 'description': 'Aggregates over a given property of the objects in a collection, calculating the sum, min, max, mean, sample standard deviation, sample variance, total standard deviation and total variance of the selected property.', 'returns': 'Object', 'type': 'Algorithm', 'hidden': False, 'name': 'AggregateFeatureCollection.stats'})
# AggregateFeatureCollection.sum
# Aggregates over a given property of the objects in a collection,
# calculating the sum of the values of the selected property.
#
# Args:
#   collection: The collection to aggregate over.
#   property: The property to use from each element of the
#       collection.
signatures.append({'args': [{'description': 'The collection to aggregate over.', 'name': 'collection', 'type': 'FeatureCollection'}, {'description': 'The property to use from each element of the collection.', 'name': 'property', 'type': 'String'}], 'description': 'Aggregates over a given property of the objects in a collection, calculating the sum of the values of the selected property.', 'returns': 'Object', 'type': 'Algorithm', 'hidden': False, 'name': 'AggregateFeatureCollection.sum'})
# AggregateFeatureCollection.total_sd
# Aggregates over a given property of the objects in a collection,
# calculating the total std. deviation of the values of the selected
# property.
#
# Args:
#   collection: The collection to aggregate over.
#   property: The property to use from each element of the
#       collection.
signatures.append({'args': [{'description': 'The collection to aggregate over.', 'name': 'collection', 'type': 'FeatureCollection'}, {'description': 'The property to use from each element of the collection.', 'name': 'property', 'type': 'String'}], 'description': 'Aggregates over a given property of the objects in a collection, calculating the total std. deviation of the values of the selected property.', 'returns': 'Object', 'type': 'Algorithm', 'hidden': False, 'name': 'AggregateFeatureCollection.total_sd'})
# AggregateFeatureCollection.total_var
# Aggregates over a given property of the objects in a collection,
# calculating the total variance of the values of the selected property.
#
# Args:
#   collection: The collection to aggregate over.
#   property: The property to use from each element of the
#       collection.
signatures.append({'args': [{'description': 'The collection to aggregate over.', 'name': 'collection', 'type': 'FeatureCollection'}, {'description': 'The property to use from each element of the collection.', 'name': 'property', 'type': 'String'}], 'description': 'Aggregates over a given property of the objects in a collection, calculating the total variance of the values of the selected property.', 'returns': 'Object', 'type': 'Algorithm', 'hidden': False, 'name': 'AggregateFeatureCollection.total_var'})
# Annotation
# Creates a Annotation.
#
# Args:
#   attributes
#   style
#   transforms
#   children
signatures.append({'args': [{'name': 'attributes', 'type': 'Object'}, {'default': None, 'name': 'style', 'optional': True, 'type': 'Dictionary'}, {'default': None, 'name': 'transforms', 'optional': True, 'type': 'List'}, {'default': None, 'name': 'children', 'optional': True, 'type': 'List'}], 'description': 'Creates a Annotation.', 'returns': 'Annotation', 'type': 'Algorithm', 'hidden': True, 'name': 'Annotation'})
# Annotation.append
# Append src as a child of dst.
#
# Args:
#   dst
#   src: An annotation or a List of annotations to add as children of
#       dst.
signatures.append({'args': [{'name': 'dst', 'type': 'Annotation'}, {'description': 'An annotation or a List of annotations to add as children of dst.', 'name': 'src', 'type': 'Object'}], 'description': 'Append src as a child of dst.', 'returns': 'Annotation', 'type': 'Algorithm', 'hidden': False, 'name': 'Annotation.append'})
# Annotation.attr
# Apply additional attributes to an annotation.
#
# Args:
#   annotation
#   attr
signatures.append({'args': [{'name': 'annotation', 'type': 'Annotation'}, {'name': 'attr', 'type': 'Dictionary'}], 'description': 'Apply additional attributes to an annotation.', 'returns': 'Annotation', 'type': 'Algorithm', 'hidden': False, 'name': 'Annotation.attr'})
# Annotation.circle
# Creates a circle annotation.
#
# Args:
#   cx: The x-axis coordinate of the center of the circle.
#   cy: The y-axis coordinate of the center of the circle.
#   r: The radius of the circle.
signatures.append({'args': [{'description': 'The x-axis coordinate of the center of the circle.', 'name': 'cx', 'type': 'Float'}, {'description': 'The y-axis coordinate of the center of the circle.', 'name': 'cy', 'type': 'Float'}, {'description': 'The radius of the circle.', 'name': 'r', 'type': 'Float'}], 'description': 'Creates a circle annotation.', 'returns': 'Annotation', 'type': 'Algorithm', 'hidden': False, 'name': 'Annotation.circle'})
# Annotation.ellipse
# Creates an ellipse annotation.
#
# Args:
#   cx: The x-axis coordinate of the center of the ellipse.
#   cy: The y-axis coordinate of the center of the ellipse.
#   rx: The x-axis radius of the ellipse.
#   ry: The y-axis radius of the ellipse.
signatures.append({'args': [{'description': 'The x-axis coordinate of the center of the ellipse.', 'name': 'cx', 'type': 'Float'}, {'description': 'The y-axis coordinate of the center of the ellipse.', 'name': 'cy', 'type': 'Float'}, {'description': 'The x-axis radius of the ellipse.', 'name': 'rx', 'type': 'Float'}, {'description': 'The y-axis radius of the ellipse.', 'name': 'ry', 'type': 'Float'}], 'description': 'Creates an ellipse annotation.', 'returns': 'Annotation', 'type': 'Algorithm', 'hidden': False, 'name': 'Annotation.ellipse'})
# Annotation.rect
# Creates a rectangle annotation.
#
# Args:
#   x: The x-axis coordinate of the upper-left corner of the rectangle.
#   y: The y-axis coordinate of the upper-left corner of the rectangle.
#   width: The width of the rectangle.
#   height: The height of the rectangle.
#   fill: The color with which to fill the rectangle.
#   radius: For rounded rectangles, the radius of the circle to
#       used to round off corners of the rectangle.
signatures.append({'args': [{'description': 'The x-axis coordinate of the upper-left corner of the rectangle.', 'name': 'x', 'type': 'Float'}, {'description': 'The y-axis coordinate of the upper-left corner of the rectangle.', 'name': 'y', 'type': 'Float'}, {'description': 'The width of the rectangle.', 'name': 'width', 'type': 'Float'}, {'description': 'The height of the rectangle.', 'name': 'height', 'type': 'Float'}, {'default': None, 'description': 'The color with which to fill the rectangle.', 'name': 'fill', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'For rounded rectangles, the radius of the circle to used to round off corners of the rectangle.', 'name': 'radius', 'optional': True, 'type': 'Float'}], 'description': 'Creates a rectangle annotation.', 'returns': 'Annotation', 'type': 'Algorithm', 'hidden': False, 'name': 'Annotation.rect'})
# Annotation.style
# Apply a style to an annotation.
#
# Args:
#   annotation
#   style
signatures.append({'args': [{'name': 'annotation', 'type': 'Annotation'}, {'name': 'style', 'type': 'Dictionary'}], 'description': 'Apply a style to an annotation.', 'returns': 'Annotation', 'type': 'Algorithm', 'hidden': False, 'name': 'Annotation.style'})
# Annotation.svg
# Creates a SVG container. Any annotations added to the container are
# positioned relative to the container's x and y position, and inherit any
# styles applied to the container.
#
# Args:
#   x: The x-axis coordinate of the upper-left corner.
#   y: The y-axis coordinate of the upper-left corner.
signatures.append({'args': [{'description': 'The x-axis coordinate of the upper-left corner.', 'name': 'x', 'type': 'Float'}, {'description': 'The y-axis coordinate of the upper-left corner.', 'name': 'y', 'type': 'Float'}], 'description': "Creates a SVG container. Any annotations added to the container are positioned relative to the container's x and y position, and inherit any styles applied to the container.", 'returns': 'Annotation', 'type': 'Algorithm', 'hidden': False, 'name': 'Annotation.svg'})
# Annotation.text
# Creates a text annotation.
#
# Args:
#   x: The x-axis coordinate for the start of the text.
#   y: The y-axis coordinate for the start of the text.
#   text: The text to render.
#   fontSize: The size of the font to use in rendering the text
#       (in pixels).
signatures.append({'args': [{'description': 'The x-axis coordinate for the start of the text.', 'name': 'x', 'type': 'Float'}, {'description': 'The y-axis coordinate for the start of the text.', 'name': 'y', 'type': 'Float'}, {'description': 'The text to render.', 'name': 'text', 'type': 'String'}, {'default': None, 'description': 'The size of the font to use in rendering the text (in pixels).', 'name': 'fontSize', 'optional': True, 'type': 'Float'}], 'description': 'Creates a text annotation.', 'returns': 'Annotation', 'type': 'Algorithm', 'hidden': False, 'name': 'Annotation.text'})
# Array
# Returns an array with the given coordinates.
#
# Args:
#   values: An existing array to cast, or a number/list of
#       numbers/nested list of numbers of any depth to create an
#       array from. For nested lists, all inner arrays at the same
#       depth must have the same length, and numbers may only be
#       present at the deepest level.
#   pixelType: The type of each number in the values argument.
#       If the pixel type is not provided, it will be inferred
#       from the numbers in 'values'. If there aren't any
#       numbers in 'values', this type must be provided.
signatures.append({'args': [{'description': 'An existing array to cast, or a number/list of numbers/nested list of numbers of any depth to create an array from. For nested lists, all inner arrays at the same depth must have the same length, and numbers may only be present at the deepest level.', 'name': 'values', 'type': 'Object'}, {'default': None, 'description': "The type of each number in the values argument. If the pixel type is not provided, it will be inferred from the numbers in 'values'. If there aren't any numbers in 'values', this type must be provided.", 'name': 'pixelType', 'optional': True, 'type': 'PixelType'}], 'description': 'Returns an array with the given coordinates.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array'})
# Array.abs
# On an element-wise basis, computes the absolute value of the input.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, computes the absolute value of the input.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.abs'})
# Array.accum
# Accumulates elements of an array along the given axis, by setting each
# element of the result to the reduction of elements along that axis up to
# and including the current position. May be used to make a cumulative sum, a
# monotonically increasing sequence, etc.
#
# Args:
#   array: Array to accumulate.
#   axis: Axis along which to perform the accumulation.
#   reducer: Reducer to accumulate values. Default is SUM, to
#       produce the cumulative sum of each vector along the given
#       axis.
signatures.append({'args': [{'description': 'Array to accumulate.', 'name': 'array', 'type': 'Array'}, {'description': 'Axis along which to perform the accumulation.', 'name': 'axis', 'type': 'Integer'}, {'default': None, 'description': 'Reducer to accumulate values. Default is SUM, to produce the cumulative sum of each vector along the given axis.', 'name': 'reducer', 'optional': True, 'type': 'Reducer'}], 'description': 'Accumulates elements of an array along the given axis, by setting each element of the result to the reduction of elements along that axis up to and including the current position. May be used to make a cumulative sum, a monotonically increasing sequence, etc.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.accum'})
# Array.acos
# On an element-wise basis, computes the arc cosine in radians of the input.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, computes the arc cosine in radians of the input.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.acos'})
# Array.add
# On an element-wise basis, adds the first value to the second.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Array'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Array'}], 'description': 'On an element-wise basis, adds the first value to the second.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.add'})
# Array.and
# On an element-wise basis, returns 1 iff both values are non-zero.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Array'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Array'}], 'description': 'On an element-wise basis, returns 1 iff both values are non-zero.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.and'})
# Array.asin
# On an element-wise basis, computes the arc sine in radians of the input.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, computes the arc sine in radians of the input.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.asin'})
# Array.atan
# On an element-wise basis, computes the arc tangent in radians of the input.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, computes the arc tangent in radians of the input.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.atan'})
# Array.atan2
# On an element-wise basis, calculates the angle formed by the 2D vector [x,
# y].
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Array'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Array'}], 'description': 'On an element-wise basis, calculates the angle formed by the 2D vector [x, y].', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.atan2'})
# Array.bitCount
# On an element-wise basis, calculates the number of one-bits in the 64-bit
# two's complement binary representation of the input.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': "On an element-wise basis, calculates the number of one-bits in the 64-bit two's complement binary representation of the input.", 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.bitCount'})
# Array.bitsToArray
# Convert the bits of an integer to an Array.  The array has as many elements
# as the position of the highest set bit, or a single 0 for a value of 0.
#
# Args:
#   input
signatures.append({'args': [{'name': 'input', 'type': 'Number'}], 'description': 'Convert the bits of an integer to an Array.  The array has as many elements as the position of the highest set bit, or a single 0 for a value of 0.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.bitsToArray'})
# Array.bitwiseAnd
# On an element-wise basis, calculates the bitwise AND of the input values.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Array'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Array'}], 'description': 'On an element-wise basis, calculates the bitwise AND of the input values.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.bitwiseAnd'})
# Array.bitwiseNot
# On an element-wise basis, calculates the bitwise NOT of the input, in the
# smallest signed integer type that can hold the input.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, calculates the bitwise NOT of the input, in the smallest signed integer type that can hold the input.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.bitwiseNot'})
# Array.bitwiseOr
# On an element-wise basis, calculates the bitwise OR of the input values.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Array'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Array'}], 'description': 'On an element-wise basis, calculates the bitwise OR of the input values.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.bitwiseOr'})
# Array.bitwiseXor
# On an element-wise basis, calculates the bitwise XOR of the input values.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Array'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Array'}], 'description': 'On an element-wise basis, calculates the bitwise XOR of the input values.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.bitwiseXor'})
# Array.bitwise_and
# On an element-wise basis, calculates the bitwise AND of the input values.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Array'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Array'}], 'description': 'On an element-wise basis, calculates the bitwise AND of the input values.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.bitwise_and'})
# Array.bitwise_not
# On an element-wise basis, calculates the bitwise NOT of the input, in the
# smallest signed integer type that can hold the input.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, calculates the bitwise NOT of the input, in the smallest signed integer type that can hold the input.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.bitwise_not'})
# Array.bitwise_or
# On an element-wise basis, calculates the bitwise OR of the input values.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Array'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Array'}], 'description': 'On an element-wise basis, calculates the bitwise OR of the input values.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.bitwise_or'})
# Array.bitwise_xor
# On an element-wise basis, calculates the bitwise XOR of the input values.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Array'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Array'}], 'description': 'On an element-wise basis, calculates the bitwise XOR of the input values.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.bitwise_xor'})
# Array.byte
# On an element-wise basis, casts the input value to an unsigned 8-bit
# integer.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, casts the input value to an unsigned 8-bit integer.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.byte'})
# Array.cat
# Concatenates multiple arrays into a single array along the given axis.
# Each array must have the same dimensionality and the same length on all
# axes except the concatenation axis.
#
# Args:
#   arrays: Arrays to concatenate.
#   axis: Axis to concatenate along.
signatures.append({'args': [{'description': 'Arrays to concatenate.', 'name': 'arrays', 'type': 'List'}, {'default': 0, 'description': 'Axis to concatenate along.', 'name': 'axis', 'optional': True, 'type': 'Integer'}], 'description': 'Concatenates multiple arrays into a single array along the given axis.  Each array must have the same dimensionality and the same length on all axes except the concatenation axis.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.cat'})
# Array.cbrt
# On an element-wise basis, computes the cubic root of the input.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, computes the cubic root of the input.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.cbrt'})
# Array.ceil
# On an element-wise basis, computes the smallest integer greater than or
# equal to the input.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, computes the smallest integer greater than or equal to the input.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.ceil'})
# Array.cos
# On an element-wise basis, computes the cosine of the input in radians.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, computes the cosine of the input in radians.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.cos'})
# Array.cosh
# On an element-wise basis, computes the hyperbolic cosine of the input.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, computes the hyperbolic cosine of the input.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.cosh'})
# Array.cut
# Cut an array along one or more axes.
#
# Args:
#   array: The array to cut.
#   position: Cut an array along one or more axes.  The positions
#       args specifies either a single value for each axis of the
#       array, or -1, indicating the whole axis.  The output will
#       be an array that has the same dimensions as the input,
#       with a length of 1 on each axis that was not -1 in the
#       positions array.
signatures.append({'args': [{'description': 'The array to cut.', 'name': 'array', 'type': 'Array'}, {'description': 'Cut an array along one or more axes.  The positions args specifies either a single value for each axis of the array, or -1, indicating the whole axis.  The output will be an array that has the same dimensions as the input, with a length of 1 on each axis that was not -1 in the positions array.', 'name': 'position', 'type': 'List'}], 'description': 'Cut an array along one or more axes.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.cut'})
# Array.digamma
# On an element-wise basis, computes the digamma function of the input.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, computes the digamma function of the input.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.digamma'})
# Array.divide
# On an element-wise basis, divides the first value by the second, returning
# 0 for division by 0.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Array'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Array'}], 'description': 'On an element-wise basis, divides the first value by the second, returning 0 for division by 0.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.divide'})
# Array.dotProduct
# Compute the dot product between two 1-D arrays.
#
# Args:
#   array1: The first 1-D array.
#   array2: The second 1-D array.
signatures.append({'args': [{'description': 'The first 1-D array.', 'name': 'array1', 'type': 'Array'}, {'description': 'The second 1-D array.', 'name': 'array2', 'type': 'Array'}], 'description': 'Compute the dot product between two 1-D arrays.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.dotProduct'})
# Array.double
# On an element-wise basis, casts the input value to a 64-bit float.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, casts the input value to a 64-bit float.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.double'})
# Array.eigen
# Computes the real eigenvectors and eigenvalues of a square 2D array of A
# rows and A columns. Returns an array with A rows and A+1 columns, where
# each row contains an eigenvalue in the first column, and the corresponding
# eigenvector in the remaining A columns. The rows are sorted by eigenvalue,
# in descending order.
#
# Args:
#   input: A square, 2D array from which to compute the eigenvalue
#       decomposition.
signatures.append({'args': [{'description': 'A square, 2D array from which to compute the eigenvalue decomposition.', 'name': 'input', 'type': 'Array'}], 'description': 'Computes the real eigenvectors and eigenvalues of a square 2D array of A rows and A columns. Returns an array with A rows and A+1 columns, where each row contains an eigenvalue in the first column, and the corresponding eigenvector in the remaining A columns. The rows are sorted by eigenvalue, in descending order.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.eigen'})
# Array.eq
# On an element-wise basis, returns 1 iff the first value is equal to the
# second.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Array'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Array'}], 'description': 'On an element-wise basis, returns 1 iff the first value is equal to the second.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.eq'})
# Array.erf
# On an element-wise basis, computes the error function of the input.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, computes the error function of the input.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.erf'})
# Array.erfInv
# On an element-wise basis, computes the inverse error function of the input.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, computes the inverse error function of the input.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.erfInv'})
# Array.erfc
# On an element-wise basis, computes the complementary error function of the
# input.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, computes the complementary error function of the input.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.erfc'})
# Array.erfcInv
# On an element-wise basis, computes the inverse complementary error function
# of the input.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, computes the inverse complementary error function of the input.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.erfcInv'})
# Array.exp
# On an element-wise basis, computes the Euler's number e raised to the power
# of the input.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': "On an element-wise basis, computes the Euler's number e raised to the power of the input.", 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.exp'})
# Array.first
# On an element-wise basis, selects the value of the first value.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Array'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Array'}], 'description': 'On an element-wise basis, selects the value of the first value.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.first'})
# Array.firstNonZero
# On an element-wise basis, selects the first value if it is non-zero, and
# the second value otherwise.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Array'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Array'}], 'description': 'On an element-wise basis, selects the first value if it is non-zero, and the second value otherwise.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.firstNonZero'})
# Array.first_nonzero
# On an element-wise basis, selects the first value if it is non-zero, and
# the second value otherwise.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Array'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Array'}], 'description': 'On an element-wise basis, selects the first value if it is non-zero, and the second value otherwise.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.first_nonzero'})
# Array.float
# On an element-wise basis, casts the input value to a 32-bit float.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, casts the input value to a 32-bit float.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.float'})
# Array.floor
# On an element-wise basis, computes the largest integer less than or equal
# to the input.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, computes the largest integer less than or equal to the input.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.floor'})
# Array.gamma
# On an element-wise basis, computes the gamma function of the input.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, computes the gamma function of the input.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.gamma'})
# Array.gammainc
# On an element-wise basis, calculates the regularized lower incomplete Gamma
# function (&gamma;(x,a).
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Array'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Array'}], 'description': 'On an element-wise basis, calculates the regularized lower incomplete Gamma function (&gamma;(x,a).', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.gammainc'})
# Array.get
# Extracts the value at the given position from the input array.
#
# Args:
#   array: The array to extract from.
#   position: The coordinates of the element to get.
signatures.append({'args': [{'description': 'The array to extract from.', 'name': 'array', 'type': 'Array'}, {'description': 'The coordinates of the element to get.', 'name': 'position', 'type': 'List'}], 'description': 'Extracts the value at the given position from the input array.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.get'})
# Array.gt
# On an element-wise basis, returns 1 iff the first value is greater than the
# second.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Array'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Array'}], 'description': 'On an element-wise basis, returns 1 iff the first value is greater than the second.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.gt'})
# Array.gte
# On an element-wise basis, returns 1 iff the first value is greater than or
# equal to the second.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Array'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Array'}], 'description': 'On an element-wise basis, returns 1 iff the first value is greater than or equal to the second.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.gte'})
# Array.hypot
# On an element-wise basis, calculates the magnitude of the 2D vector [x, y].
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Array'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Array'}], 'description': 'On an element-wise basis, calculates the magnitude of the 2D vector [x, y].', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.hypot'})
# Array.identity
# Creates a 2D identity matrix of the given size.
#
# Args:
#   size: The length of each axis.
signatures.append({'args': [{'description': 'The length of each axis.', 'name': 'size', 'type': 'Integer'}], 'description': 'Creates a 2D identity matrix of the given size.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.identity'})
# Array.int
# On an element-wise basis, casts the input value to a signed 32-bit integer.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, casts the input value to a signed 32-bit integer.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.int'})
# Array.int16
# On an element-wise basis, casts the input value to a signed 16-bit integer.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, casts the input value to a signed 16-bit integer.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.int16'})
# Array.int32
# On an element-wise basis, casts the input value to a signed 32-bit integer.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, casts the input value to a signed 32-bit integer.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.int32'})
# Array.int64
# On an element-wise basis, casts the input value to a signed 64-bit integer.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, casts the input value to a signed 64-bit integer.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.int64'})
# Array.int8
# On an element-wise basis, casts the input value to a signed 8-bit integer.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, casts the input value to a signed 8-bit integer.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.int8'})
# Array.lanczos
# On an element-wise basis, computes the Lanczos approximation of the input.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, computes the Lanczos approximation of the input.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.lanczos'})
# Array.leftShift
# On an element-wise basis, calculates the left shift of v1 by v2 bits.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Array'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Array'}], 'description': 'On an element-wise basis, calculates the left shift of v1 by v2 bits.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.leftShift'})
# Array.left_shift
# On an element-wise basis, calculates the left shift of v1 by v2 bits.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Array'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Array'}], 'description': 'On an element-wise basis, calculates the left shift of v1 by v2 bits.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.left_shift'})
# Array.length
# Returns a 1-D EEArray containing the length of each dimension of the given
# EEArray.
#
# Args:
#   array: The array from which to extract the axis lengths.
signatures.append({'args': [{'description': 'The array from which to extract the axis lengths.', 'name': 'array', 'type': 'Array'}], 'description': 'Returns a 1-D EEArray containing the length of each dimension of the given EEArray.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.length'})
# Array.log
# On an element-wise basis, computes the natural logarithm of the input.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, computes the natural logarithm of the input.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.log'})
# Array.log10
# On an element-wise basis, computes the base-10 logarithm of the input.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, computes the base-10 logarithm of the input.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.log10'})
# Array.long
# On an element-wise basis, casts the input value to a signed 64-bit integer.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, casts the input value to a signed 64-bit integer.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.long'})
# Array.lt
# On an element-wise basis, returns 1 iff the first value is less than the
# second.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Array'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Array'}], 'description': 'On an element-wise basis, returns 1 iff the first value is less than the second.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.lt'})
# Array.lte
# On an element-wise basis, returns 1 iff the first value is less than or
# equal to the second.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Array'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Array'}], 'description': 'On an element-wise basis, returns 1 iff the first value is less than or equal to the second.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.lte'})
# Array.mask
# Creates a subarray by slicing out each position in an input array that is
# parallel to a non-zero element of the given mask array.
#
# Args:
#   input: Array to mask.
#   mask: Mask array.
signatures.append({'args': [{'description': 'Array to mask.', 'name': 'input', 'type': 'Array'}, {'description': 'Mask array.', 'name': 'mask', 'type': 'Array'}], 'description': 'Creates a subarray by slicing out each position in an input array that is parallel to a non-zero element of the given mask array.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.mask'})
# Array.matrixCholeskyDecomposition
# Calculates the Cholesky decomposition of a matrix. The Cholesky
# decomposition is a decomposition into the form L*L' where L is a lower
# triangular matrix. The input must be a symmetric positive-definite matrix.
# Returns a dictionary with 1 entry named 'L'.
#
# Args:
#   array: The array to decompose.
signatures.append({'args': [{'description': 'The array to decompose.', 'name': 'array', 'type': 'Array'}], 'description': "Calculates the Cholesky decomposition of a matrix. The Cholesky decomposition is a decomposition into the form L*L' where L is a lower triangular matrix. The input must be a symmetric positive-definite matrix. Returns a dictionary with 1 entry named 'L'.", 'returns': 'Dictionary', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.matrixCholeskyDecomposition'})
# Array.matrixDeterminant
# Computes the determinant of the matrix.
#
# Args:
#   input: The array to compute on.
signatures.append({'args': [{'description': 'The array to compute on.', 'name': 'input', 'type': 'Array'}], 'description': 'Computes the determinant of the matrix.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.matrixDeterminant'})
# Array.matrixDiagonal
# Computes the diagonal of the matrix in a single column.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'Computes the diagonal of the matrix in a single column.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.matrixDiagonal'})
# Array.matrixFnorm
# Computes the Frobenius norm of the matrix.
#
# Args:
#   input: The array to compute on.
signatures.append({'args': [{'description': 'The array to compute on.', 'name': 'input', 'type': 'Array'}], 'description': 'Computes the Frobenius norm of the matrix.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.matrixFnorm'})
# Array.matrixInverse
# Computes the inverse of the matrix.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'Computes the inverse of the matrix.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.matrixInverse'})
# Array.matrixLUDecomposition
# Calculates the LU matrix decomposition such that P×input=L×U, where L is
# lower triangular (with unit diagonal terms), U is upper triangular and P is
# a partial pivot permutation matrix. The input matrix must be square.
# Returns a dictionary with entries named 'L', 'U' and 'P'.
#
# Args:
#   array: The array to decompose.
signatures.append({'args': [{'description': 'The array to decompose.', 'name': 'array', 'type': 'Array'}], 'description': "Calculates the LU matrix decomposition such that P×input=L×U, where L is lower triangular (with unit diagonal terms), U is upper triangular and P is a partial pivot permutation matrix. The input matrix must be square. Returns a dictionary with entries named 'L', 'U' and 'P'.", 'returns': 'Dictionary', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.matrixLUDecomposition'})
# Array.matrixMultiply
# Returns the matrix multiplication A*B.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Array'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Array'}], 'description': 'Returns the matrix multiplication A*B.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.matrixMultiply'})
# Array.matrixPseudoInverse
# Computes the Moore-Penrose pseudoinverse of the matrix.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'Computes the Moore-Penrose pseudoinverse of the matrix.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.matrixPseudoInverse'})
# Array.matrixQRDecomposition
# Calculates the QR-decomposition of a matrix into two matrices Q and R such
# that input = QR, where Q is orthogonal, and R is upper triangular. Returns
# a dictionary with entries named 'Q' and 'R'.
#
# Args:
#   array: The array to decompose.
signatures.append({'args': [{'description': 'The array to decompose.', 'name': 'array', 'type': 'Array'}], 'description': "Calculates the QR-decomposition of a matrix into two matrices Q and R such that input = QR, where Q is orthogonal, and R is upper triangular. Returns a dictionary with entries named 'Q' and 'R'.", 'returns': 'Dictionary', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.matrixQRDecomposition'})
# Array.matrixSingularValueDecomposition
# Calculates the Singular Value Decomposition of the input matrix into
# U×S×V', such that U and V are orthogonal and S is diagonal. Returns a
# dictionary with entries named 'U', 'S' and 'V'.
#
# Args:
#   array: The array to decompose.
signatures.append({'args': [{'description': 'The array to decompose.', 'name': 'array', 'type': 'Array'}], 'description': "Calculates the Singular Value Decomposition of the input matrix into U×S×V', such that U and V are orthogonal and S is diagonal. Returns a dictionary with entries named 'U', 'S' and 'V'.", 'returns': 'Dictionary', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.matrixSingularValueDecomposition'})
# Array.matrixSolve
# Solves for x in the matrix equation A*x=B, finding a least-squares solution
# if A is overdetermined.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Array'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Array'}], 'description': 'Solves for x in the matrix equation A*x=B, finding a least-squares solution if A is overdetermined.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.matrixSolve'})
# Array.matrixToDiag
# Computes a square diagonal matrix from a single column matrix.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'Computes a square diagonal matrix from a single column matrix.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.matrixToDiag'})
# Array.matrixTrace
# Computes the trace of the matrix.
#
# Args:
#   input: The array to compute on.
signatures.append({'args': [{'description': 'The array to compute on.', 'name': 'input', 'type': 'Array'}], 'description': 'Computes the trace of the matrix.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.matrixTrace'})
# Array.matrixTranspose
# Transposes two dimensions of an array.
#
# Args:
#   array: Array to transpose.
#   axis1: First axis to swap.
#   axis2: Second axis to swap.
signatures.append({'args': [{'description': 'Array to transpose.', 'name': 'array', 'type': 'Array'}, {'default': 0, 'description': 'First axis to swap.', 'name': 'axis1', 'optional': True, 'type': 'Integer'}, {'default': 1, 'description': 'Second axis to swap.', 'name': 'axis2', 'optional': True, 'type': 'Integer'}], 'description': 'Transposes two dimensions of an array.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.matrixTranspose'})
# Array.max
# On an element-wise basis, selects the maximum of the first and second
# values.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Array'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Array'}], 'description': 'On an element-wise basis, selects the maximum of the first and second values.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.max'})
# Array.min
# On an element-wise basis, selects the minimum of the first and second
# values.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Array'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Array'}], 'description': 'On an element-wise basis, selects the minimum of the first and second values.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.min'})
# Array.mod
# On an element-wise basis, calculates the remainder of the first value
# divided by the second.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Array'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Array'}], 'description': 'On an element-wise basis, calculates the remainder of the first value divided by the second.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.mod'})
# Array.multiply
# On an element-wise basis, multiplies the first value by the second.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Array'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Array'}], 'description': 'On an element-wise basis, multiplies the first value by the second.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.multiply'})
# Array.neq
# On an element-wise basis, returns 1 iff the first value is not equal to the
# second.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Array'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Array'}], 'description': 'On an element-wise basis, returns 1 iff the first value is not equal to the second.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.neq'})
# Array.not
# On an element-wise basis, returns 0 if the input is non-zero, and 1
# otherwise.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, returns 0 if the input is non-zero, and 1 otherwise.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.not'})
# Array.or
# On an element-wise basis, returns 1 iff either input value is non-zero.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Array'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Array'}], 'description': 'On an element-wise basis, returns 1 iff either input value is non-zero.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.or'})
# Array.pow
# On an element-wise basis, raises the first value to the power of the
# second.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Array'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Array'}], 'description': 'On an element-wise basis, raises the first value to the power of the second.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.pow'})
# Array.project
# Projects an array to a lower dimensional space by specifying the axes to
# retain. Dropped axes must be at most length 1.
#
# Args:
#   array: Array to project.
#   axes: The axes to project onto. Other axes will be discarded, and
#       must be at most length 1.
signatures.append({'args': [{'description': 'Array to project.', 'name': 'array', 'type': 'Array'}, {'description': 'The axes to project onto. Other axes will be discarded, and must be at most length 1.', 'name': 'axes', 'type': 'List'}], 'description': 'Projects an array to a lower dimensional space by specifying the axes to retain. Dropped axes must be at most length 1.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.project'})
# Array.reduce
# Apply a reducer to an array by collapsing all the input values along each
# specified axis into a single output value computed by the reducer.
#
# Args:
#   array: The array.
#   reducer: The reducer to apply
#   axes: The list of axes over which to reduce.  The output will
#       have a length of 1 in all these axes.
#   fieldAxis: The axis for the reducer's input and output
#       fields.  Only required if the reducer has multiple
#       inputs or outputs.
signatures.append({'args': [{'description': 'The array.', 'name': 'array', 'type': 'Array'}, {'description': 'The reducer to apply', 'name': 'reducer', 'type': 'Reducer'}, {'description': 'The list of axes over which to reduce.  The output will have a length of 1 in all these axes.', 'name': 'axes', 'type': 'List'}, {'default': None, 'description': "The axis for the reducer's input and output fields.  Only required if the reducer has multiple inputs or outputs.", 'name': 'fieldAxis', 'optional': True, 'type': 'Integer'}], 'description': 'Apply a reducer to an array by collapsing all the input values along each specified axis into a single output value computed by the reducer.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.reduce'})
# Array.repeat
# Repeats the array along the given axis. The result will have the shape of
# the input, except length along the repeated axis will be multiplied by the
# given number of copies.
#
# Args:
#   array: Array to repeat.
#   axis: The axis along which to repeat the array.
#   copies: The number of copies of this array to concatenate along
#       the given axis.
signatures.append({'args': [{'description': 'Array to repeat.', 'name': 'array', 'type': 'Array'}, {'default': 0, 'description': 'The axis along which to repeat the array.', 'name': 'axis', 'optional': True, 'type': 'Integer'}, {'default': 2, 'description': 'The number of copies of this array to concatenate along the given axis.', 'name': 'copies', 'optional': True, 'type': 'Integer'}], 'description': 'Repeats the array along the given axis. The result will have the shape of the input, except length along the repeated axis will be multiplied by the given number of copies.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.repeat'})
# Array.rightShift
# On an element-wise basis, calculates the signed right shift of v1 by v2
# bits.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Array'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Array'}], 'description': 'On an element-wise basis, calculates the signed right shift of v1 by v2 bits.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.rightShift'})
# Array.right_shift
# On an element-wise basis, calculates the signed right shift of v1 by v2
# bits.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Array'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Array'}], 'description': 'On an element-wise basis, calculates the signed right shift of v1 by v2 bits.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.right_shift'})
# Array.round
# On an element-wise basis, computes the integer nearest to the input.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, computes the integer nearest to the input.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.round'})
# Array.short
# On an element-wise basis, casts the input value to a signed 16-bit integer.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, casts the input value to a signed 16-bit integer.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.short'})
# Array.sin
# On an element-wise basis, computes the sine of the input in radians.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, computes the sine of the input in radians.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.sin'})
# Array.sinh
# On an element-wise basis, computes the hyperbolic sine of the input.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, computes the hyperbolic sine of the input.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.sinh'})
# Array.slice
# Creates a subarray by slicing out each position along the given axis from
# the 'start' (inclusive) to 'end' (exclusive) by increments of 'step'. The
# result will have as many dimensions as the input, and the same length in
# all directions except the slicing axis, where the length will be the number
# of positions from 'start' to 'end' by 'step' that are in range of the input
# array's length along 'axis'. This means the result can be length 0 along
# the given axis if start=end, or if the start or end values are entirely out
# of range.
#
# Args:
#   array: Array to slice.
#   axis: The axis to slice on.
#   start: The coordinate of the first slice (inclusive) along
#       'axis'. Negative numbers are used to position the start of
#       slicing relative to the end of the array, where -1 starts at
#       the last position on the axis, -2 starts at the next to last
#       position, etc.
#   end: The coordinate (exclusive) at which to stop taking slices. By
#       default this will be the length of the given axis. Negative
#       numbers are used to position the end of slicing relative to
#       the end of the array, where -1 will exclude the last position,
#       -2 will exclude the last two positions, etc.
#   step: The separation between slices along 'axis'; a slice will be
#       taken at each whole multiple of 'step' from 'start'
#       (inclusive) to 'end' (exclusive). Must be positive.
signatures.append({'args': [{'description': 'Array to slice.', 'name': 'array', 'type': 'Array'}, {'default': 0, 'description': 'The axis to slice on.', 'name': 'axis', 'optional': True, 'type': 'Integer'}, {'default': 0, 'description': "The coordinate of the first slice (inclusive) along 'axis'. Negative numbers are used to position the start of slicing relative to the end of the array, where -1 starts at the last position on the axis, -2 starts at the next to last position, etc.", 'name': 'start', 'optional': True, 'type': 'Integer'}, {'default': None, 'description': 'The coordinate (exclusive) at which to stop taking slices. By default this will be the length of the given axis. Negative numbers are used to position the end of slicing relative to the end of the array, where -1 will exclude the last position, -2 will exclude the last two positions, etc.', 'name': 'end', 'optional': True, 'type': 'Integer'}, {'default': 1, 'description': "The separation between slices along 'axis'; a slice will be taken at each whole multiple of 'step' from 'start' (inclusive) to 'end' (exclusive). Must be positive.", 'name': 'step', 'optional': True, 'type': 'Integer'}], 'description': "Creates a subarray by slicing out each position along the given axis from the 'start' (inclusive) to 'end' (exclusive) by increments of 'step'. The result will have as many dimensions as the input, and the same length in all directions except the slicing axis, where the length will be the number of positions from 'start' to 'end' by 'step' that are in range of the input array's length along 'axis'. This means the result can be length 0 along the given axis if start=end, or if the start or end values are entirely out of range.", 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.slice'})
# Array.sort
# Sorts elements of the array along one axis.
#
# Args:
#   array: Array image to sort.
#   keys: Optional keys to sort by. If not provided, the values are
#       used as the keys. The keys can only have multiple elements
#       along one axis, which determines the direction to sort in.
signatures.append({'args': [{'description': 'Array image to sort.', 'name': 'array', 'type': 'Array'}, {'default': None, 'description': 'Optional keys to sort by. If not provided, the values are used as the keys. The keys can only have multiple elements along one axis, which determines the direction to sort in.', 'name': 'keys', 'optional': True, 'type': 'Array'}], 'description': 'Sorts elements of the array along one axis.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.sort'})
# Array.sqrt
# On an element-wise basis, computes the square root of the input.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, computes the square root of the input.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.sqrt'})
# Array.subtract
# On an element-wise basis, subtracts the second value from the first.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Array'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Array'}], 'description': 'On an element-wise basis, subtracts the second value from the first.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.subtract'})
# Array.tan
# On an element-wise basis, computes the tangent of the input in radians.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, computes the tangent of the input in radians.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.tan'})
# Array.tanh
# On an element-wise basis, computes the hyperbolic tangent of the input.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, computes the hyperbolic tangent of the input.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.tanh'})
# Array.toByte
# On an element-wise basis, casts the input value to an unsigned 8-bit
# integer.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, casts the input value to an unsigned 8-bit integer.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.toByte'})
# Array.toDouble
# On an element-wise basis, casts the input value to a 64-bit float.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, casts the input value to a 64-bit float.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.toDouble'})
# Array.toFloat
# On an element-wise basis, casts the input value to a 32-bit float.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, casts the input value to a 32-bit float.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.toFloat'})
# Array.toInt
# On an element-wise basis, casts the input value to a signed 32-bit integer.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, casts the input value to a signed 32-bit integer.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.toInt'})
# Array.toInt16
# On an element-wise basis, casts the input value to a signed 16-bit integer.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, casts the input value to a signed 16-bit integer.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.toInt16'})
# Array.toInt32
# On an element-wise basis, casts the input value to a signed 32-bit integer.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, casts the input value to a signed 32-bit integer.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.toInt32'})
# Array.toInt64
# On an element-wise basis, casts the input value to a signed 64-bit integer.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, casts the input value to a signed 64-bit integer.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.toInt64'})
# Array.toInt8
# On an element-wise basis, casts the input value to a signed 8-bit integer.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, casts the input value to a signed 8-bit integer.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.toInt8'})
# Array.toList
# Turns an Array into a list of lists of numbers.
#
# Args:
#   array: Array to convert.
signatures.append({'args': [{'description': 'Array to convert.', 'name': 'array', 'type': 'Array'}], 'description': 'Turns an Array into a list of lists of numbers.', 'returns': 'List', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.toList'})
# Array.toLong
# On an element-wise basis, casts the input value to a signed 64-bit integer.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, casts the input value to a signed 64-bit integer.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.toLong'})
# Array.toShort
# On an element-wise basis, casts the input value to a signed 16-bit integer.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, casts the input value to a signed 16-bit integer.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.toShort'})
# Array.toUint16
# On an element-wise basis, casts the input value to an unsigned 16-bit
# integer.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, casts the input value to an unsigned 16-bit integer.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.toUint16'})
# Array.toUint32
# On an element-wise basis, casts the input value to an unsigned 32-bit
# integer.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, casts the input value to an unsigned 32-bit integer.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.toUint32'})
# Array.toUint8
# On an element-wise basis, casts the input value to an unsigned 8-bit
# integer.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, casts the input value to an unsigned 8-bit integer.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.toUint8'})
# Array.transpose
# Transposes two dimensions of an array.
#
# Args:
#   array: Array to transpose.
#   axis1: First axis to swap.
#   axis2: Second axis to swap.
signatures.append({'args': [{'description': 'Array to transpose.', 'name': 'array', 'type': 'Array'}, {'default': 0, 'description': 'First axis to swap.', 'name': 'axis1', 'optional': True, 'type': 'Integer'}, {'default': 1, 'description': 'Second axis to swap.', 'name': 'axis2', 'optional': True, 'type': 'Integer'}], 'description': 'Transposes two dimensions of an array.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.transpose'})
# Array.trigamma
# On an element-wise basis, computes the trigamma function of the input.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, computes the trigamma function of the input.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.trigamma'})
# Array.uint16
# On an element-wise basis, casts the input value to an unsigned 16-bit
# integer.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, casts the input value to an unsigned 16-bit integer.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.uint16'})
# Array.uint32
# On an element-wise basis, casts the input value to an unsigned 32-bit
# integer.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, casts the input value to an unsigned 32-bit integer.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.uint32'})
# Array.uint8
# On an element-wise basis, casts the input value to an unsigned 8-bit
# integer.
#
# Args:
#   input: The input array.
signatures.append({'args': [{'description': 'The input array.', 'name': 'input', 'type': 'Array'}], 'description': 'On an element-wise basis, casts the input value to an unsigned 8-bit integer.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Array.uint8'})
# BACCINI/ModisComposite
# Creates composites of MODIS MCD43A4 ("Nadir BRDF-Adjusted Reflectance
# 16-Day") 500m global mosaics, based on an algorithm by Alessandro Baccini,
# Mark Friedl and Damien Sulla-Menashe.
#
# Args:
#   lastYear: Date range end point is the mosaic's last day.
#   reflectance: The MCD43A4 collection.
#   quality: The MCD43A2 collection.
#   numberOfYears: The number of years to draw images from.
#   firstDayOfYear: The start of the season (1-360).
#   numberOfDaysPerYear: The length of the season
#       (8-368).
#   numberOfQualityLevels: Only use pixels of lower
#       quality level (1-5).
signatures.append({'args': [{'description': "Date range end point is the mosaic's last day.", 'name': 'lastYear', 'type': 'DateRange'}, {'description': 'The MCD43A4 collection.', 'name': 'reflectance', 'type': 'ImageCollection'}, {'description': 'The MCD43A2 collection.', 'name': 'quality', 'type': 'ImageCollection'}, {'description': 'The number of years to draw images from.', 'name': 'numberOfYears', 'type': 'Integer'}, {'description': 'The start of the season (1-360).', 'name': 'firstDayOfYear', 'type': 'Integer'}, {'description': 'The length of the season (8-368).', 'name': 'numberOfDaysPerYear', 'type': 'Integer'}, {'description': 'Only use pixels of lower quality level (1-5).', 'name': 'numberOfQualityLevels', 'type': 'Integer'}], 'description': 'Creates composites of MODIS MCD43A4 ("Nadir BRDF-Adjusted Reflectance 16-Day") 500m global mosaics, based on an algorithm by Alessandro Baccini, Mark Friedl and Damien Sulla-Menashe.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': True, 'name': 'BACCINI/ModisComposite'})
# Baccini.modisComposite
# Creates composites of MODIS MCD43A4 ("Nadir BRDF-Adjusted Reflectance
# 16-Day") 500m global mosaics, based on an algorithm by Alessandro Baccini,
# Mark Friedl and Damien Sulla-Menashe.
#
# Args:
#   lastYear: Date range end point is the mosaic's last day.
#   reflectance: The MCD43A4 collection.
#   quality: The MCD43A2 collection.
#   numberOfYears: The number of years to draw images from.
#   firstDayOfYear: The start of the season (1-360).
#   numberOfDaysPerYear: The length of the season
#       (8-368).
#   numberOfQualityLevels: Only use pixels of lower
#       quality level (1-5).
signatures.append({'args': [{'description': "Date range end point is the mosaic's last day.", 'name': 'lastYear', 'type': 'DateRange'}, {'description': 'The MCD43A4 collection.', 'name': 'reflectance', 'type': 'ImageCollection'}, {'description': 'The MCD43A2 collection.', 'name': 'quality', 'type': 'ImageCollection'}, {'description': 'The number of years to draw images from.', 'name': 'numberOfYears', 'type': 'Integer'}, {'description': 'The start of the season (1-360).', 'name': 'firstDayOfYear', 'type': 'Integer'}, {'description': 'The length of the season (8-368).', 'name': 'numberOfDaysPerYear', 'type': 'Integer'}, {'description': 'Only use pixels of lower quality level (1-5).', 'name': 'numberOfQualityLevels', 'type': 'Integer'}], 'description': 'Creates composites of MODIS MCD43A4 ("Nadir BRDF-Adjusted Reflectance 16-Day") 500m global mosaics, based on an algorithm by Alessandro Baccini, Mark Friedl and Damien Sulla-Menashe.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': True, 'name': 'Baccini.modisComposite'})
# BetterDateRangeCollection
# Returns a collection of objects with 'system:index' and 'date_range'
# properties in a defined sequence at regular intervals, suitable for mapping
# over.
#
# Args:
#   start: The start of the date range (inclusive).
#   end: The end of the date range (exclusive).
#   delta: The time interval between successive date ranges, in
#       units specified by 'units'. If negative, 'start' must be
#       after 'end'.
#   unit: The units in which 'delta' is specified:One of 'year',
#       'month' 'week', 'day', 'hour', 'minute', or 'second'.
#   resetAtYearBoundaries: If true, the start time
#       of the intervals will align to the start of
#       each year (but the end times will still be
#       delta * units).
#   format: A pattern to use to format the system:index, as
#       described at  http://joda-time.sourceforge.net/apidocs/org/
#       joda/time/format/DateTimeFormat.html.If omitted will use a
#       portion of the format 'YYYYMMddHHmmss', up to the specified
#       'unit' (ie: for unit='year' format will default to 'YYYY',
#       and for unit='day', format will default to 'YYYYMMdd'.
#       When 'unit' is 'week' format defaultsto 'YYYYMMdd'.
signatures.append({'args': [{'description': 'The start of the date range (inclusive).', 'name': 'start', 'type': 'Date'}, {'description': 'The end of the date range (exclusive).', 'name': 'end', 'type': 'Date'}, {'default': 1, 'description': "The time interval between successive date ranges, in units specified by 'units'. If negative, 'start' must be after 'end'.", 'name': 'delta', 'optional': True, 'type': 'Integer'}, {'default': 'days', 'description': "The units in which 'delta' is specified:One of 'year', 'month' 'week', 'day', 'hour', 'minute', or 'second'.", 'name': 'unit', 'optional': True, 'type': 'String'}, {'default': False, 'description': 'If true, the start time of the intervals will align to the start of each year (but the end times will still be delta * units).', 'name': 'resetAtYearBoundaries', 'optional': True, 'type': 'Boolean'}, {'default': None, 'description': "A pattern to use to format the system:index, as described at  http://joda-time.sourceforge.net/apidocs/org/joda/time/format/DateTimeFormat.html.If omitted will use a portion of the format 'YYYYMMddHHmmss', up to the specified 'unit' (ie: for unit='year' format will default to 'YYYY', and for unit='day', format will default to 'YYYYMMdd'.  When 'unit' is 'week' format defaultsto 'YYYYMMdd'.", 'name': 'format', 'optional': True, 'type': 'String'}], 'description': "Returns a collection of objects with 'system:index' and 'date_range' properties in a defined sequence at regular intervals, suitable for mapping over.", 'returns': 'FeatureCollection', 'type': 'Algorithm', 'hidden': True, 'name': 'BetterDateRangeCollection'})
# Blob
# Loads a Blob from a Google Cloud Storage URL.
#
# Args:
#   url: The Blob's Google Cloud Storage URL.
signatures.append({'args': [{'description': "The Blob's Google Cloud Storage URL.", 'name': 'url', 'type': 'String'}], 'description': 'Loads a Blob from a Google Cloud Storage URL.', 'returns': 'Blob', 'type': 'Algorithm', 'hidden': False, 'name': 'Blob'})
# Blob.string
# Returns the contents of the blob as a String.
#
# Args:
#   blob
#   encoding
signatures.append({'args': [{'name': 'blob', 'type': 'Blob'}, {'default': None, 'name': 'encoding', 'optional': True, 'type': 'String'}], 'description': 'Returns the contents of the blob as a String.', 'returns': 'String', 'type': 'Algorithm', 'hidden': False, 'name': 'Blob.string'})
# Blob.url
# Returns the Blob's Google Cloud Storage URL.
#
# Args:
#   blob
signatures.append({'args': [{'name': 'blob', 'type': 'Blob'}], 'description': "Returns the Blob's Google Cloud Storage URL.", 'returns': 'String', 'type': 'Algorithm', 'hidden': False, 'name': 'Blob.url'})
# CannyEdgeDetector
# Applies the Canny edge detection algorithm to an image. The output is an
# image whose bands have the same names as the input bands, and in which non-
# zero values indicate edges, and the magnitude of the value is the gradient
# magnitude.
#
# Args:
#   image: The image on which to apply edge detection.
#   threshold: Threshold value. The pixel is only considered for
#       edge detection if the gradient magnitude is higher than
#       this threshold.
#   sigma: Sigma value for a gaussian filter applied before edge
#       detection. 0 means apply no filtering.
signatures.append({'args': [{'description': 'The image on which to apply edge detection.', 'name': 'image', 'type': 'Image'}, {'description': 'Threshold value. The pixel is only considered for edge detection if the gradient magnitude is higher than this threshold.', 'name': 'threshold', 'type': 'Float'}, {'default': 1.0, 'description': 'Sigma value for a gaussian filter applied before edge detection. 0 means apply no filtering.', 'name': 'sigma', 'optional': True, 'type': 'Float'}], 'description': 'Applies the Canny edge detection algorithm to an image. The output is an image whose bands have the same names as the input bands, and in which non-zero values indicate edges, and the magnitude of the value is the gradient magnitude.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'CannyEdgeDetector'})
# CcdcCoefficients
# Provides Continuous Change Detection and Classification (CCDC) coefficients
# by fitting a simple piecewise linear model to a given image collection. The
# linear model used for each fit is 'Y = A + B*t + C*sin(season(t)) +
# D*cos(season(t))', where 't' is the start time of the image in years, and
# season(t) returns the phase of the year from 0 to 2*PI. The result is a 3D
# array per pixel, with axis 0 having as many elements as there are pieces in
# the piecewise fit, axis 1 having as many elements as there are bands, and
# axis 2 having length 7, for each parameter of the fit: 1. Start time in
# years (e.g. 2005.678.) 2. End time in years (e.g. 2006.0123.) 3. Total root
# mean square error (RMSE) summed from each separately fit band's RMSE. 4. A
# coefficient. 5. B coefficient. 6. C coefficient. 7. D coefficient. The
# function is fit for each band separately, and the RMSE is summed from all
# the fits. If the sum exceeds the given RMSE, that sample is considered
# disturbed. If there are 'disturbanceWindow' disturbed samples in a row, the
# last good fit that did not involve disturbed samples is added to the output
# array, and a new fit is started after the last disturbed sample. The
# samples in the disturbed area are thus not part of any of the fit results.
#
# Args:
#   timeSeries: Collection from which to extract trends. Must
#       be sorted by time in ascending order.
#   rmse: Sum of the root mean square error (RMSE) from all band fits
#       at which we consider the set of fits to have become
#       disturbed.
#   disturbanceWindow: Consecutive disturbances to force
#       reclassifying the terrain.
signatures.append({'args': [{'description': 'Collection from which to extract trends. Must be sorted by time in ascending order.', 'name': 'timeSeries', 'type': 'ImageCollection'}, {'description': 'Sum of the root mean square error (RMSE) from all band fits at which we consider the set of fits to have become disturbed.', 'name': 'rmse', 'type': 'Float'}, {'default': 3, 'description': 'Consecutive disturbances to force reclassifying the terrain.', 'name': 'disturbanceWindow', 'optional': True, 'type': 'Integer'}], 'description': "Provides Continuous Change Detection and Classification (CCDC) coefficients by fitting a simple piecewise linear model to a given image collection.\nThe linear model used for each fit is 'Y = A + B*t + C*sin(season(t)) + D*cos(season(t))', where 't' is the start time of the image in years, and season(t) returns the phase of the year from 0 to 2*PI.\nThe result is a 3D array per pixel, with axis 0 having as many elements as there are pieces in the piecewise fit, axis 1 having as many elements as there are bands, and axis 2 having length 7, for each parameter of the fit:\n1. Start time in years (e.g. 2005.678.)\n2. End time in years (e.g. 2006.0123.)\n3. Total root mean square error (RMSE) summed from each separately fit band's RMSE.\n4. A coefficient.\n5. B coefficient.\n6. C coefficient.\n7. D coefficient.\nThe function is fit for each band separately, and the RMSE is summed from all the fits. If the sum exceeds the given RMSE, that sample is considered disturbed. If there are 'disturbanceWindow' disturbed samples in a row, the last good fit that did not involve disturbed samples is added to the output array, and a new fit is started after the last disturbed sample. The samples in the disturbed area are thus not part of any of the fit results.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': True, 'name': 'CcdcCoefficients'})
# Classifier.TrainingContainer
# INTERNAL
#
# Args:
#   classifier
signatures.append({'args': [{'name': 'classifier', 'type': 'Classifier'}], 'description': 'INTERNAL', 'returns': 'Image', 'type': 'Algorithm', 'hidden': True, 'name': 'Classifier.TrainingContainer'})
# Classifier.cart
# Creates an empty CART classifier. See:   "Classification and Regression
# Trees,"   L. Breiman, J. Friedman, R. Olshen, C. Stone   Chapman and Hall,
# 1984.
#
# Args:
#   crossvalidationFactor: The cross-validation
#       factor for pruning.
#   maxDepth: Do not grow initial tree deeper than this many
#       levels.
#   minLeafPopulation: Only create nodes whose training
#       set contains at least this many points.
#   minSplitPoplulation: Do not split unless node has
#       at least this many points.
#   minSplitCost: Do not split if training set cost less than
#       this.
#   prune: Whether to skip pruning; i.e., only impose stopping
#       criteria while growing the tree.
#   pruneErrorTolerance: The standard error threshold
#       to use in determining the simplest tree whose
#       accuracy is comparable to the minimum cost-
#       complexity tree.
#   quantizationResolution: The quantization
#       resolution for numerical features.
#   quantizationMargin: The margin reserved by
#       quantizer to avoid overload, as a fraction of
#       the range observed in the training data.
#   randomSeed: The randomization seed.
signatures.append({'args': [{'default': 10, 'description': 'The cross-validation factor for pruning.', 'name': 'crossvalidationFactor', 'optional': True, 'type': 'Integer'}, {'default': 10, 'description': 'Do not grow initial tree deeper than this many levels.', 'name': 'maxDepth', 'optional': True, 'type': 'Integer'}, {'default': 1, 'description': 'Only create nodes whose training set contains at least this many points.', 'name': 'minLeafPopulation', 'optional': True, 'type': 'Integer'}, {'default': 1, 'description': 'Do not split unless node has at least this many points.', 'name': 'minSplitPoplulation', 'optional': True, 'type': 'Integer'}, {'default': 1e-10, 'description': 'Do not split if training set cost less than this.', 'name': 'minSplitCost', 'optional': True, 'type': 'Float'}, {'default': False, 'description': 'Whether to skip pruning; i.e., only impose stopping criteria while growing the tree.', 'name': 'prune', 'optional': True, 'type': 'Boolean'}, {'default': 0.5, 'description': 'The standard error threshold to use in determining the simplest tree whose accuracy is comparable to the minimum cost-complexity tree.', 'name': 'pruneErrorTolerance', 'optional': True, 'type': 'Float'}, {'default': 100, 'description': 'The quantization resolution for numerical features.', 'name': 'quantizationResolution', 'optional': True, 'type': 'Integer'}, {'default': 0.1, 'description': 'The margin reserved by quantizer to avoid overload, as a fraction of the range observed in the training data.', 'name': 'quantizationMargin', 'optional': True, 'type': 'Float'}, {'default': 0, 'description': 'The randomization seed.', 'name': 'randomSeed', 'optional': True, 'type': 'Integer'}], 'description': 'Creates an empty CART classifier. See:\n  "Classification and Regression Trees,"\n  L. Breiman, J. Friedman, R. Olshen, C. Stone\n  Chapman and Hall, 1984.', 'returns': 'Classifier', 'type': 'Algorithm', 'hidden': False, 'name': 'Classifier.cart'})
# Classifier.confusionMatrix
# Computes a 2D confusion matrix for a classifier based on its training data.
# Axis 1 (the rows) of the matrix correspond to the input classes, and Axis 0
# (the columns) to the output classes.
#
# Args:
#   classifier: The classifier to use.
signatures.append({'args': [{'description': 'The classifier to use.', 'name': 'classifier', 'type': 'Classifier'}], 'description': 'Computes a 2D confusion matrix for a classifier based on its training data. Axis 1 (the rows) of the matrix correspond to the input classes, and Axis 0 (the columns) to the output classes.', 'returns': 'ConfusionMatrix', 'type': 'Algorithm', 'hidden': False, 'name': 'Classifier.confusionMatrix'})
# Classifier.continuousNaiveBayes
# Creates an empty Continuous Naive Bayes classifier.
#
# Args:
#   lambda: A smoothing lambda. Used to avoid assigning zero
#       probability to classes not seen during training, instead
#       using lambda / (lambda * nFeatures).
signatures.append({'args': [{'default': 0.001, 'description': 'A smoothing lambda. Used to avoid assigning zero probability to classes not seen during training, instead using lambda / (lambda * nFeatures).', 'name': 'lambda', 'optional': True, 'type': 'Float'}], 'description': 'Creates an empty Continuous Naive Bayes classifier.', 'returns': 'Classifier', 'type': 'Algorithm', 'hidden': False, 'name': 'Classifier.continuousNaiveBayes'})
# Classifier.decisionTree
# Creates a classifier that applies the given decision tree.
#
# Args:
#   treeString: The decision tree, specified in the text format
#       generated by R and other similar tools.
signatures.append({'args': [{'description': 'The decision tree, specified in the text format generated by R and other similar tools.', 'name': 'treeString', 'type': 'String'}], 'description': 'Creates a classifier that applies the given decision tree.', 'returns': 'Classifier', 'type': 'Algorithm', 'hidden': False, 'name': 'Classifier.decisionTree'})
# Classifier.explain
# Describe the results of a trained classifier.
#
# Args:
#   classifier: The classifier to describe.
signatures.append({'args': [{'description': 'The classifier to describe.', 'name': 'classifier', 'type': 'Classifier'}], 'description': 'Describe the results of a trained classifier.', 'returns': 'Dictionary', 'type': 'Algorithm', 'hidden': False, 'name': 'Classifier.explain'})
# Classifier.gmoLinearRegression
# Creates an empty linear regression. This regression supports L1 and L2
# regularization as well as a smoothed L1 regularization using a logistic
# loss function. Note that the model used by this regression does not include
# a bias by default and a constant value should be included if a bias is
# required (it is suggested).  This classifier only supports REGRESSION mode.
#
# Args:
#   weight1: The weight for L1 regularization. Larger weight leads
#       to heavier regularization.
#   weight2: The weight for L2 regularization. Larger weight leads
#       to heavier regularization.
#   epsilon: The epsilon for stopping optimization.
#   maxIterations: The maximum number of iterations.
#   smooth: Use a logistic loss function for the L1 regularization.
signatures.append({'args': [{'default': 0.0, 'description': 'The weight for L1 regularization. Larger weight leads to heavier regularization.', 'name': 'weight1', 'optional': True, 'type': 'Float'}, {'default': 0.0, 'description': 'The weight for L2 regularization. Larger weight leads to heavier regularization.', 'name': 'weight2', 'optional': True, 'type': 'Float'}, {'default': 1e-05, 'description': 'The epsilon for stopping optimization.', 'name': 'epsilon', 'optional': True, 'type': 'Float'}, {'default': 100, 'description': 'The maximum number of iterations.', 'name': 'maxIterations', 'optional': True, 'type': 'Integer'}, {'default': False, 'description': 'Use a logistic loss function for the L1 regularization.', 'name': 'smooth', 'optional': True, 'type': 'Boolean'}], 'description': 'Creates an empty linear regression. This regression supports L1 and L2 regularization as well as a smoothed L1 regularization using a logistic loss function. Note that the model used by this regression does not include a bias by default and a constant value should be included if a bias is required (it is suggested).  This classifier only supports REGRESSION mode.', 'returns': 'Classifier', 'type': 'Algorithm', 'hidden': False, 'name': 'Classifier.gmoLinearRegression'})
# Classifier.gmoMaxEnt
# Creates an empty GMO Maximum Entropy classifier. See:   "Efﬁcient Large-
# Scale Distributed Training of Conditional Maximum Entropy Models,"   G.
# Mann, R. McDonald, M. Mohri, N. Silberman, D. Walker.
#
# Args:
#   weight1: The weight for L1 regularization.
#   weight2: The weight for L2 regularization.
#   epsilon: The epsilon for stopping optimization.
#   minIterations: The minimum number of iterations of
#       optimizer.
#   maxIterations: The maximum number of iterations of
#       optimizer.
signatures.append({'args': [{'default': 0.0, 'description': 'The weight for L1 regularization.', 'name': 'weight1', 'optional': True, 'type': 'Float'}, {'default': 1e-05, 'description': 'The weight for L2 regularization.', 'name': 'weight2', 'optional': True, 'type': 'Float'}, {'default': 1e-05, 'description': 'The epsilon for stopping optimization.', 'name': 'epsilon', 'optional': True, 'type': 'Float'}, {'default': 0, 'description': 'The minimum number of iterations of optimizer.', 'name': 'minIterations', 'optional': True, 'type': 'Integer'}, {'default': 100, 'description': 'The maximum number of iterations of optimizer.', 'name': 'maxIterations', 'optional': True, 'type': 'Integer'}], 'description': 'Creates an empty GMO Maximum Entropy classifier. See:\n  "Efﬁcient Large-Scale Distributed Training of Conditional Maximum Entropy Models,"\n  G. Mann, R. McDonald, M. Mohri, N. Silberman, D. Walker.', 'returns': 'Classifier', 'type': 'Algorithm', 'hidden': False, 'name': 'Classifier.gmoMaxEnt'})
# Classifier.ikpamir
# Creates an IKPAMIR (Intersection Kernel Passive-Aggressive Method for
# Information Retrieval) classifier. See:   "Classification using
# Intersection Kernel Support Vector Machinesis Efficient"   S. Maji, A.
# Berg, J. Malik
#
# Args:
#   numBins: The number of histogram bins per dimension.
#   learningRate: The rate of learning from each example.
#   epochs: The maximum number of epochs.
signatures.append({'args': [{'default': 10, 'description': 'The number of histogram bins per dimension.', 'name': 'numBins', 'optional': True, 'type': 'Integer'}, {'default': 0.1, 'description': 'The rate of learning from each example.', 'name': 'learningRate', 'optional': True, 'type': 'Float'}, {'default': 5, 'description': 'The maximum number of epochs.', 'name': 'epochs', 'optional': True, 'type': 'Integer'}], 'description': 'Creates an IKPAMIR (Intersection Kernel Passive-Aggressive Method for Information Retrieval) classifier. See:\n  "Classification using Intersection Kernel Support Vector Machinesis Efficient"\n  S. Maji, A. Berg, J. Malik', 'returns': 'Classifier', 'type': 'Algorithm', 'hidden': False, 'name': 'Classifier.ikpamir'})
# Classifier.minimumDistance
# Creates a minimum distance classifier for the given distance metric.
#
# Args:
#   metric: The distance metric to use.  Options are:   'euclidean'
#       - euclidean distance from the unnormalized class mean.
#       'cosine' - spectral angle from the unnormalized class mean.
#       'mahalanobis' - Mahalanobis distance from the class mean.
signatures.append({'args': [{'default': 'euclidean', 'description': "The distance metric to use.  Options are:\n  'euclidean' - euclidean distance from the unnormalized class mean.\n  'cosine' - spectral angle from the unnormalized class mean.\n  'mahalanobis' - Mahalanobis distance from the class mean.", 'name': 'metric', 'optional': True, 'type': 'String'}], 'description': 'Creates a minimum distance classifier for the given distance metric.', 'returns': 'Classifier', 'type': 'Algorithm', 'hidden': False, 'name': 'Classifier.minimumDistance'})
# Classifier.mode
# Returns the classifier mode: CLASSIFICATION, REGRESSION or PROBABILITY.
#
# Args:
#   classifier
signatures.append({'args': [{'name': 'classifier', 'type': 'Classifier'}], 'description': 'Returns the classifier mode: CLASSIFICATION, REGRESSION or PROBABILITY.', 'returns': 'String', 'type': 'Algorithm', 'hidden': False, 'name': 'Classifier.mode'})
# Classifier.naiveBayes
# Creates an empty Fast Naive Bayes classifier.
#
# Args:
#   lambda: A smoothing lambda. Used to avoid assigning zero
#       probability to classes not seen during training, instead
#       using lambda / (lambda * nFeatures).
signatures.append({'args': [{'default': 1e-06, 'description': 'A smoothing lambda. Used to avoid assigning zero probability to classes not seen during training, instead using lambda / (lambda * nFeatures).', 'name': 'lambda', 'optional': True, 'type': 'Float'}], 'description': 'Creates an empty Fast Naive Bayes classifier.', 'returns': 'Classifier', 'type': 'Algorithm', 'hidden': False, 'name': 'Classifier.naiveBayes'})
# Classifier.pegasos
# Creates a Classifier.
#
# Args:
#   kernelType
#   lossFunction
#   lambda
#   iterations
#   subsetSize
#   regularizationNorm
#   multiGamma
#   useExponentiated
#   polyDegree
#   polyBias
#   rbfGamma
signatures.append({'args': [{'name': 'kernelType', 'type': 'String'}, {'name': 'lossFunction', 'type': 'String'}, {'name': 'lambda', 'type': 'Float'}, {'name': 'iterations', 'type': 'Integer'}, {'name': 'subsetSize', 'type': 'Integer'}, {'name': 'regularizationNorm', 'type': 'Float'}, {'name': 'multiGamma', 'type': 'Float'}, {'default': None, 'name': 'useExponentiated', 'optional': True, 'type': 'Boolean'}, {'default': None, 'name': 'polyDegree', 'optional': True, 'type': 'Integer'}, {'default': None, 'name': 'polyBias', 'optional': True, 'type': 'Float'}, {'default': None, 'name': 'rbfGamma', 'optional': True, 'type': 'Float'}], 'description': 'Creates a Classifier.', 'returns': 'Classifier', 'type': 'Algorithm', 'hidden': True, 'name': 'Classifier.pegasos'})
# Classifier.pegasosGaussian
# Creates an empty gaussian Pegasos classifier. See:   "Pegasos (Primal
# Estimated sub-GrAdient SOlver for SVM)"   S. Shalev-Shwartz, Y. Singer, N.
# Srebro, A. Cotter
#
# Args:
#   rbfGamma: The gamma value of the Gaussian kernel.
#   lossFunction: The loss function to use. Valid values are:
#       'HingeSum', 'HingeMax', 'LogSum' and 'LogMax'
#   lambda: The regularization parameter of SVM (λ).
#   iterations: The number of iterations (T). When set to 0
#       (default), the number of training iterations is
#       automatically set to 5 * training data size (~5
#       epochs).
#   subsetSize: The subset size (k), i.e. the number of random
#       samples to process on each iteration.
#   regularizationNorm: The norm of w for
#       regularization.
#   multiGamma: The gamma value for the loss function in multi-
#       class classification.
signatures.append({'args': [{'default': 1.0, 'description': 'The gamma value of the Gaussian kernel.', 'name': 'rbfGamma', 'optional': True, 'type': 'Float'}, {'default': 'HingeSum', 'description': "The loss function to use. Valid values are: 'HingeSum', 'HingeMax', 'LogSum' and 'LogMax'", 'name': 'lossFunction', 'optional': True, 'type': 'String'}, {'default': 0.001, 'description': 'The regularization parameter of SVM (λ).', 'name': 'lambda', 'optional': True, 'type': 'Float'}, {'default': 0, 'description': 'The number of iterations (T). When set to 0 (default), the number of training iterations is automatically set to 5 * training data size (~5 epochs).', 'name': 'iterations', 'optional': True, 'type': 'Integer'}, {'default': 1, 'description': 'The subset size (k), i.e. the number of random samples to process on each iteration.', 'name': 'subsetSize', 'optional': True, 'type': 'Integer'}, {'default': 1.0, 'description': 'The norm of w for regularization.', 'name': 'regularizationNorm', 'optional': True, 'type': 'Float'}, {'default': 0.01, 'description': 'The gamma value for the loss function in multi-class classification.', 'name': 'multiGamma', 'optional': True, 'type': 'Float'}], 'description': 'Creates an empty gaussian Pegasos classifier. See:\n  "Pegasos (Primal Estimated sub-GrAdient SOlver for SVM)"\n  S. Shalev-Shwartz, Y. Singer, N. Srebro, A. Cotter', 'returns': 'Classifier', 'type': 'Algorithm', 'hidden': False, 'name': 'Classifier.pegasosGaussian'})
# Classifier.pegasosLinear
# Creates an empty linear Pegasos classifier. See:   "Pegasos (Primal
# Estimated sub-GrAdient SOlver for SVM)"   S. Shalev-Shwartz, Y. Singer, N.
# Srebro, A. Cotter
#
# Args:
#   useExponentiated: Whether to use exponentiated
#       update.
#   lossFunction: The loss function to use. Valid values are:
#       'HingeSum', 'HingeMax', 'LogSum' and 'LogMax'
#   lambda: The regularization parameter of SVM (λ).
#   iterations: The number of iterations (T). When set to 0
#       (default), the number of training iterations is
#       automatically set to 5 * training data size (~5
#       epochs).
#   subsetSize: The subset size (k), i.e. the number of random
#       samples to process on each iteration.
#   regularizationNorm: The norm of w for
#       regularization.
#   multiGamma: The gamma value for the loss function in multi-
#       class classification.
signatures.append({'args': [{'default': False, 'description': 'Whether to use exponentiated update.', 'name': 'useExponentiated', 'optional': True, 'type': 'Boolean'}, {'default': 'HingeSum', 'description': "The loss function to use. Valid values are: 'HingeSum', 'HingeMax', 'LogSum' and 'LogMax'", 'name': 'lossFunction', 'optional': True, 'type': 'String'}, {'default': 0.001, 'description': 'The regularization parameter of SVM (λ).', 'name': 'lambda', 'optional': True, 'type': 'Float'}, {'default': 0, 'description': 'The number of iterations (T). When set to 0 (default), the number of training iterations is automatically set to 5 * training data size (~5 epochs).', 'name': 'iterations', 'optional': True, 'type': 'Integer'}, {'default': 1, 'description': 'The subset size (k), i.e. the number of random samples to process on each iteration.', 'name': 'subsetSize', 'optional': True, 'type': 'Integer'}, {'default': 1.0, 'description': 'The norm of w for regularization.', 'name': 'regularizationNorm', 'optional': True, 'type': 'Float'}, {'default': 0.01, 'description': 'The gamma value for the loss function in multi-class classification.', 'name': 'multiGamma', 'optional': True, 'type': 'Float'}], 'description': 'Creates an empty linear Pegasos classifier. See:\n  "Pegasos (Primal Estimated sub-GrAdient SOlver for SVM)"\n  S. Shalev-Shwartz, Y. Singer, N. Srebro, A. Cotter', 'returns': 'Classifier', 'type': 'Algorithm', 'hidden': False, 'name': 'Classifier.pegasosLinear'})
# Classifier.pegasosPolynomial
# Creates an empty polynomial Pegasos classifier. See:   "Pegasos (Primal
# Estimated sub-GrAdient SOlver for SVM)"   S. Shalev-Shwartz, Y. Singer, N.
# Srebro, A. Cotter
#
# Args:
#   polyDegree: The degree of the Polynomial kernel.
#   polyBias: The bias of the Polynomial kernel.
#   lossFunction: The loss function to use. Valid values are:
#       'HingeSum', 'HingeMax', 'LogSum' and 'LogMax'
#   lambda: The regularization parameter of SVM (λ).
#   iterations: The number of iterations (T). When set to 0
#       (default), the number of training iterations is
#       automatically set to 5 * training data size (~5
#       epochs).
#   subsetSize: The subset size (k), i.e. the number of random
#       samples to process on each iteration.
#   regularizationNorm: The norm of w for
#       regularization.
#   multiGamma: The gamma value for the loss function in multi-
#       class classification.
signatures.append({'args': [{'default': 3, 'description': 'The degree of the Polynomial kernel.', 'name': 'polyDegree', 'optional': True, 'type': 'Integer'}, {'default': 1.0, 'description': 'The bias of the Polynomial kernel.', 'name': 'polyBias', 'optional': True, 'type': 'Float'}, {'default': 'HingeSum', 'description': "The loss function to use. Valid values are: 'HingeSum', 'HingeMax', 'LogSum' and 'LogMax'", 'name': 'lossFunction', 'optional': True, 'type': 'String'}, {'default': 0.001, 'description': 'The regularization parameter of SVM (λ).', 'name': 'lambda', 'optional': True, 'type': 'Float'}, {'default': 0, 'description': 'The number of iterations (T). When set to 0 (default), the number of training iterations is automatically set to 5 * training data size (~5 epochs).', 'name': 'iterations', 'optional': True, 'type': 'Integer'}, {'default': 1, 'description': 'The subset size (k), i.e. the number of random samples to process on each iteration.', 'name': 'subsetSize', 'optional': True, 'type': 'Integer'}, {'default': 1.0, 'description': 'The norm of w for regularization.', 'name': 'regularizationNorm', 'optional': True, 'type': 'Float'}, {'default': 0.01, 'description': 'The gamma value for the loss function in multi-class classification.', 'name': 'multiGamma', 'optional': True, 'type': 'Float'}], 'description': 'Creates an empty polynomial Pegasos classifier. See:\n  "Pegasos (Primal Estimated sub-GrAdient SOlver for SVM)"\n  S. Shalev-Shwartz, Y. Singer, N. Srebro, A. Cotter', 'returns': 'Classifier', 'type': 'Algorithm', 'hidden': False, 'name': 'Classifier.pegasosPolynomial'})
# Classifier.perceptron
# Creates an empty Perceptron classifier. See:   "Practical Structured
# Learning Techniques for Natural Language Processing"   H. Daume III, pp.
# 9-10
#
# Args:
#   epochs: The number of training epochs.
#   averaged: Whether to use an averaged perceptron.
signatures.append({'args': [{'default': 10, 'description': 'The number of training epochs.', 'name': 'epochs', 'optional': True, 'type': 'Integer'}, {'default': True, 'description': 'Whether to use an averaged perceptron.', 'name': 'averaged', 'optional': True, 'type': 'Boolean'}], 'description': 'Creates an empty Perceptron classifier. See:\n  "Practical Structured Learning Techniques for Natural Language Processing"\n  H. Daume III, pp. 9-10', 'returns': 'Classifier', 'type': 'Algorithm', 'hidden': False, 'name': 'Classifier.perceptron'})
# Classifier.randomForest
# Creates an empty Rifle Serial classifier, which uses the Random Forest
# algorithm.
#
# Args:
#   numberOfTrees: The number of Rifle decision trees to
#       create per class.
#   variablesPerSplit: The number of variables per
#       split. If set to 0 (default), defaults to the
#       square root of the number of variables.
#   minLeafPopulation: The minimum size of a terminal
#       node.
#   bagFraction: The fraction of input to bag per tree.
#   outOfBagMode: Whether the classifier should run in out-
#       of-bag mode.
#   seed: Random seed.
signatures.append({'args': [{'default': 1, 'description': 'The number of Rifle decision trees to create per class.', 'name': 'numberOfTrees', 'optional': True, 'type': 'Integer'}, {'default': 0, 'description': 'The number of variables per split. If set to 0 (default), defaults to the square root of the number of variables.', 'name': 'variablesPerSplit', 'optional': True, 'type': 'Integer'}, {'default': 1, 'description': 'The minimum size of a terminal node.', 'name': 'minLeafPopulation', 'optional': True, 'type': 'Integer'}, {'default': 0.5, 'description': 'The fraction of input to bag per tree.', 'name': 'bagFraction', 'optional': True, 'type': 'Float'}, {'default': False, 'description': 'Whether the classifier should run in out-of-bag mode.', 'name': 'outOfBagMode', 'optional': True, 'type': 'Boolean'}, {'default': 0, 'description': 'Random seed.', 'name': 'seed', 'optional': True, 'type': 'Integer'}], 'description': 'Creates an empty Rifle Serial classifier, which uses the Random Forest algorithm.', 'returns': 'Classifier', 'type': 'Algorithm', 'hidden': False, 'name': 'Classifier.randomForest'})
# Classifier.schema
# Returns the names of the inputs used by this classifier, or null if this
# classifier has not had any training data added yet.
#
# Args:
#   classifier
signatures.append({'args': [{'name': 'classifier', 'type': 'Classifier'}], 'description': 'Returns the names of the inputs used by this classifier, or null if this classifier has not had any training data added yet.', 'returns': 'List', 'type': 'Algorithm', 'hidden': False, 'name': 'Classifier.schema'})
# Classifier.setOutputMode
# Sets the output mode.
#
# Args:
#   classifier: An input classifier.
#   mode: The output mode. One of:   - CLASSIFICATION (default): The
#       output is the class number.   - REGRESSION: The output is the
#       result of standard regression.   - PROBABILITY: The output is
#       the probability that the classification is correct. Not all
#       classifier types support REGRESSION and PROBABILITY modes.
signatures.append({'args': [{'description': 'An input classifier.', 'name': 'classifier', 'type': 'Classifier'}, {'description': 'The output mode. One of:\n  - CLASSIFICATION (default): The output is the class number.\n  - REGRESSION: The output is the result of standard regression.\n  - PROBABILITY: The output is the probability that the classification is correct.\nNot all classifier types support REGRESSION and PROBABILITY modes.', 'name': 'mode', 'type': 'String'}], 'description': 'Sets the output mode.', 'returns': 'Classifier', 'type': 'Algorithm', 'hidden': False, 'name': 'Classifier.setOutputMode'})
# Classifier.spectralRegion
# Creates a classifier that tests if its inputs lie within a polygon defined
# by a set  of coordinates in an arbitrary 2D coordinate system.  Each input
# to be classified  must have 2 values (e.g.: images must have 2 bands).  The
# result will be 1 wherever  the input values are contained within the given
# polygon and 0 otherwise.
#
# Args:
#   coordinates: The coordinates of the polygon, as a list of
#       rings. Each ring is a list of coordinate pairs (e.g.:
#       [u1, v1, u2, v2, ..., uN, vN]).  No edge may intersect
#       any other edge. The resulting classification will be a
#       1 wherever the input values are within the interior of
#       the given polygon, that is, an odd number of polygon
#       edges must be crossed to get outside the polygon and 0
#       otherwise.
#   schema: The classifier's schema.  A list of band or property
#       names that the classifier will operate on.  Since this
#       classifier doesn't undergo a training step, these have to
#       be specified manually.  Defaults to ['u', 'v'].
signatures.append({'args': [{'description': 'The coordinates of the polygon, as a list of rings. Each ring is a list of coordinate pairs (e.g.: [u1, v1, u2, v2, ..., uN, vN]).  No edge may intersect any other edge. The resulting classification will be a 1 wherever the input values are within the interior of the given polygon, that is, an odd number of polygon edges must be crossed to get outside the polygon and 0 otherwise.', 'name': 'coordinates', 'type': 'List'}, {'default': None, 'description': "The classifier's schema.  A list of band or property names that the classifier will operate on.  Since this classifier doesn't undergo a training step, these have to be specified manually.  Defaults to ['u', 'v'].", 'name': 'schema', 'optional': True, 'type': 'List'}], 'description': 'Creates a classifier that tests if its inputs lie within a polygon defined by a set  of coordinates in an arbitrary 2D coordinate system.  Each input to be classified  must have 2 values (e.g.: images must have 2 bands).  The result will be 1 wherever  the input values are contained within the given polygon and 0 otherwise.', 'returns': 'Classifier', 'type': 'Algorithm', 'hidden': False, 'name': 'Classifier.spectralRegion'})
# Classifier.svm
# Creates a Support Vector Machine classifier.
#
# Args:
#   decisionProcedure: The decision procedure to use for
#       classification. Either 'Voting' or 'Margin'. Not
#       used for regression.
#   svmType: The SVM type. One of C_SVC, NU_SVC, ONE_CLASS,
#       EPSILON_SVR or NU_SVR.
#   kernelType: The kernel type. One of LINEAR (u′×v), POLY
#       ((γ×u′×v + coef₀)ᵈᵉᵍʳᵉᵉ), RBF (exp(-γ×|u-v|²)) or
#       SIGMOID (tanh(γ×u′×v + coef₀)).
#   shrinking: Whether to use shrinking heuristics.
#   degree: The degree of polynomial. Valid for POLY kernels.
#   gamma: The gamma value in the kernel function. Defaults to the
#       reciprocal of the number of features. Valid for POLY, RBF
#       and SIGMOID kernels.
#   coef0: The coef₀ value in the kernel function. Defaults to 0.
#       Valid for POLY and SIGMOID kernels.
#   cost: The cost (C) parameter. Defaults to 1. Only valid for
#       C-SVC, epsilon-SVR, and nu-SVR.
#   nu: The nu parameter. Defaults to 0.5. Only valid for of nu-SVC,
#       one-class SVM, and nu-SVR.
#   terminationEpsilon: The termination criterion
#       tolerance (e). Defaults to 0.001. Only valid
#       for epsilon-SVR.
#   lossEpsilon: The epsilon in the loss function (p).
#       Defaults to 0.1. Only valid for epsilon-SVR.
#   oneClass: The class of the training data on which to train in
#       a one-class svm.  Defaults to 0. Only valid for one-class
#       SVM.  Possible values are 0 and 1.  The classifier output
#       is binary (0/1) and will match this class value for the
#       data determined to be in the class.
signatures.append({'args': [{'default': 'Voting', 'description': "The decision procedure to use for classification. Either 'Voting' or 'Margin'. Not used for regression.", 'name': 'decisionProcedure', 'optional': True, 'type': 'String'}, {'default': 'C_SVC', 'description': 'The SVM type. One of C_SVC, NU_SVC, ONE_CLASS, EPSILON_SVR or NU_SVR.', 'name': 'svmType', 'optional': True, 'type': 'String'}, {'default': 'LINEAR', 'description': 'The kernel type. One of LINEAR (u′×v), POLY ((γ×u′×v + coef₀)ᵈᵉᵍʳᵉᵉ), RBF (exp(-γ×|u-v|²)) or SIGMOID (tanh(γ×u′×v + coef₀)).', 'name': 'kernelType', 'optional': True, 'type': 'String'}, {'default': True, 'description': 'Whether to use shrinking heuristics.', 'name': 'shrinking', 'optional': True, 'type': 'Boolean'}, {'default': None, 'description': 'The degree of polynomial. Valid for POLY kernels.', 'name': 'degree', 'optional': True, 'type': 'Integer'}, {'default': None, 'description': 'The gamma value in the kernel function. Defaults to the reciprocal of the number of features. Valid for POLY, RBF and SIGMOID kernels.', 'name': 'gamma', 'optional': True, 'type': 'Float'}, {'default': None, 'description': 'The coef₀ value in the kernel function. Defaults to 0. Valid for POLY and SIGMOID kernels.', 'name': 'coef0', 'optional': True, 'type': 'Float'}, {'default': None, 'description': 'The cost (C) parameter. Defaults to 1. Only valid for C-SVC, epsilon-SVR, and nu-SVR.', 'name': 'cost', 'optional': True, 'type': 'Float'}, {'default': None, 'description': 'The nu parameter. Defaults to 0.5. Only valid for of nu-SVC, one-class SVM, and nu-SVR.', 'name': 'nu', 'optional': True, 'type': 'Float'}, {'default': None, 'description': 'The termination criterion tolerance (e). Defaults to 0.001. Only valid for epsilon-SVR.', 'name': 'terminationEpsilon', 'optional': True, 'type': 'Float'}, {'default': None, 'description': 'The epsilon in the loss function (p). Defaults to 0.1. Only valid for epsilon-SVR.', 'name': 'lossEpsilon', 'optional': True, 'type': 'Float'}, {'default': None, 'description': 'The class of the training data on which to train in a one-class svm.  Defaults to 0. Only valid for one-class SVM.  Possible values are 0 and 1.  The classifier output is binary (0/1) and will match this class value for the data determined to be in the class.', 'name': 'oneClass', 'optional': True, 'type': 'Integer'}], 'description': 'Creates a Support Vector Machine classifier.', 'returns': 'Classifier', 'type': 'Algorithm', 'hidden': False, 'name': 'Classifier.svm'})
# Classifier.train
# Trains the classifier on a collection of features, using the specified
# numeric properties of each feature as training data. The geometry of the
# features is ignored.
#
# Args:
#   classifier: An input classifier.
#   features: The collection to train on.
#   classProperty: The name of the property containing the
#       class value. Each feature must have this property,
#       and its value must be numeric.
#   inputProperties: The list of property names to include
#       as training data. Each feature must have all these
#       properties, and their values must be numeric.
#       This argument is optional if the input collection
#       contains a 'band_order' property, (as produced by
#       Image.sample).
#   subsampling: An optional subsampling factor, within (0,
#       1].
#   subsamplingSeed: A randomization seed to use for
#       subsampling.
signatures.append({'args': [{'description': 'An input classifier.', 'name': 'classifier', 'type': 'Classifier'}, {'description': 'The collection to train on.', 'name': 'features', 'type': 'FeatureCollection'}, {'description': 'The name of the property containing the class value. Each feature must have this property, and its value must be numeric.', 'name': 'classProperty', 'type': 'String'}, {'default': None, 'description': "The list of property names to include as training data. Each feature must have all these properties, and their values must be numeric.  This argument is optional if the input collection contains a 'band_order' property, (as produced by Image.sample).", 'name': 'inputProperties', 'optional': True, 'type': 'List'}, {'default': 1.0, 'description': 'An optional subsampling factor, within (0, 1].', 'name': 'subsampling', 'optional': True, 'type': 'Float'}, {'default': 0, 'description': 'A randomization seed to use for subsampling.', 'name': 'subsamplingSeed', 'optional': True, 'type': 'Integer'}], 'description': 'Trains the classifier on a collection of features, using the specified numeric properties of each feature as training data. The geometry of the features is ignored.', 'returns': 'Classifier', 'type': 'Algorithm', 'hidden': False, 'name': 'Classifier.train'})
# Classifier.winnow
# Creates an empty Winnow classifier. Uses an updating rule similar to the
# one described in:   "Automatically categorizing written texts by author
# gender"   M. Koppel, S. Argamon, A. Shimoni   Literary and Linguistic
# Computing 17(4), November 2002, pp. 401-412.
#
# Args:
#   epochs: The number of training epochs.
#   learningRate: The learning rate.
#   biasLearningRate: The learning rate for updating bias
#       weights.
#   margin: The "wide-margin" (or "thick"-separator) size. If this
#       is nonzero, the classifier updates the weights even when it
#       just barely got the answer right. See "Mistake-Driven
#       Learning in Text Categorization" by I. Dagan, Y. Karov, and
#       D. Roth.
signatures.append({'args': [{'default': 5, 'description': 'The number of training epochs.', 'name': 'epochs', 'optional': True, 'type': 'Integer'}, {'default': 0.1, 'description': 'The learning rate.', 'name': 'learningRate', 'optional': True, 'type': 'Float'}, {'default': 0.1, 'description': 'The learning rate for updating bias weights.', 'name': 'biasLearningRate', 'optional': True, 'type': 'Float'}, {'default': 0.2, 'description': 'The "wide-margin" (or "thick"-separator) size. If this is nonzero, the classifier updates the weights even when it just barely got the answer right. See "Mistake-Driven Learning in Text Categorization" by I. Dagan, Y. Karov, and D. Roth.', 'name': 'margin', 'optional': True, 'type': 'Float'}], 'description': 'Creates an empty Winnow classifier. Uses an updating rule similar to the one described in:\n  "Automatically categorizing written texts by author gender"\n  M. Koppel, S. Argamon, A. Shimoni\n  Literary and Linguistic Computing 17(4), November 2002, pp. 401-412.', 'returns': 'Classifier', 'type': 'Algorithm', 'hidden': False, 'name': 'Classifier.winnow'})
# Clusterer.TrainingContainer
# INTERNAL
#
# Args:
#   clusterer
signatures.append({'args': [{'name': 'clusterer', 'type': 'Clusterer'}], 'description': 'INTERNAL', 'returns': 'Image', 'type': 'Algorithm', 'hidden': True, 'name': 'Clusterer.TrainingContainer'})
# Clusterer.schema
# Returns the names of the inputs used by this Clusterer, or null if this
# Clusterer has not had any training data added yet.
#
# Args:
#   clusterer
signatures.append({'args': [{'name': 'clusterer', 'type': 'Clusterer'}], 'description': 'Returns the names of the inputs used by this Clusterer, or null if this Clusterer has not had any training data added yet.', 'returns': 'List', 'type': 'Algorithm', 'hidden': False, 'name': 'Clusterer.schema'})
# Clusterer.train
# Trains the Clusterer on a collection of features, using the specified
# numeric properties of each feature as training data. The geometry of the
# features is ignored.
#
# Args:
#   clusterer: An input Clusterer.
#   features: The collection to train on.
#   inputProperties: The list of property names to include
#       as training data. Each feature must have all these
#       properties, and their values must be numeric.
#       This argument is optional if the input collection
#       contains a 'band_order' property, (as produced by
#       Image.sample).
#   subsampling: An optional subsampling factor, within (0,
#       1].
#   subsamplingSeed: A randomization seed to use for
#       subsampling.
signatures.append({'args': [{'description': 'An input Clusterer.', 'name': 'clusterer', 'type': 'Clusterer'}, {'description': 'The collection to train on.', 'name': 'features', 'type': 'FeatureCollection'}, {'default': None, 'description': "The list of property names to include as training data. Each feature must have all these properties, and their values must be numeric.  This argument is optional if the input collection contains a 'band_order' property, (as produced by Image.sample).", 'name': 'inputProperties', 'optional': True, 'type': 'List'}, {'default': 1.0, 'description': 'An optional subsampling factor, within (0, 1].', 'name': 'subsampling', 'optional': True, 'type': 'Float'}, {'default': 0, 'description': 'A randomization seed to use for subsampling.', 'name': 'subsamplingSeed', 'optional': True, 'type': 'Integer'}], 'description': 'Trains the Clusterer on a collection of features, using the specified numeric properties of each feature as training data. The geometry of the features is ignored.', 'returns': 'Clusterer', 'type': 'Algorithm', 'hidden': False, 'name': 'Clusterer.train'})
# Clusterer.wekaCascadeKMeans
# Cascade simple k-means, selects the best k according to calinski-harabasz
# criterion. For more information see: Calinski, T. and J. Harabasz. 1974. A
# dendrite method for cluster analysis. Commun. Stat. 3: 1-27.
#
# Args:
#   minClusters: Min number of clusters.
#   maxClusters: Max number of clusters.
#   restarts: Number of restarts.
#   manual: Manually select the number of clusters.
#   init: Set whether to initialize using the probabilistic farthest
#       first like method of the k-means++ algorithm (rather than the
#       standard random selection of initial cluster centers).
#   distanceFunction: Distance function to use.  Options
#       are: Euclidean & Manhattan
#   maxIterations: Maximum number of iterations for k-means.
signatures.append({'args': [{'default': 2, 'description': 'Min number of clusters.', 'name': 'minClusters', 'optional': True, 'type': 'Integer'}, {'default': 10, 'description': 'Max number of clusters.', 'name': 'maxClusters', 'optional': True, 'type': 'Integer'}, {'default': 10, 'description': 'Number of restarts.', 'name': 'restarts', 'optional': True, 'type': 'Integer'}, {'default': False, 'description': 'Manually select the number of clusters.', 'name': 'manual', 'optional': True, 'type': 'Boolean'}, {'default': False, 'description': 'Set whether to initialize using the probabilistic farthest first like method of the k-means++ algorithm (rather than the standard random selection of initial cluster centers).', 'name': 'init', 'optional': True, 'type': 'Boolean'}, {'default': 'Euclidean', 'description': 'Distance function to use.  Options are: Euclidean & Manhattan', 'name': 'distanceFunction', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'Maximum number of iterations for k-means.', 'name': 'maxIterations', 'optional': True, 'type': 'Integer'}], 'description': 'Cascade simple k-means, selects the best k according to calinski-harabasz criterion. For more information see:\nCalinski, T. and J. Harabasz. 1974. A dendrite method for cluster analysis. Commun. Stat. 3: 1-27.', 'returns': 'Clusterer', 'type': 'Algorithm', 'hidden': False, 'name': 'Clusterer.wekaCascadeKMeans'})
# Clusterer.wekaCobweb
# Implementation of the Cobweb clustering algorithm. For more information
# see: D. Fisher (1987). Knowledge acquisition via incremental conceptual
# clustering. Machine Learning. 2(2):139-172. and J. H. Gennari, P. Langley,
# D. Fisher (1990). Models of incremental concept formation. Artificial
# Intelligence. 40:11-61.
#
# Args:
#   acuity: Acuity (minimum standard deviation).
#   cutoff: Cutoff (minimum category utility).
#   seed: Random number seed.
signatures.append({'args': [{'default': 1.0, 'description': 'Acuity (minimum standard deviation).', 'name': 'acuity', 'optional': True, 'type': 'Float'}, {'default': 0.002, 'description': 'Cutoff (minimum category utility).', 'name': 'cutoff', 'optional': True, 'type': 'Float'}, {'default': 42, 'description': 'Random number seed.', 'name': 'seed', 'optional': True, 'type': 'Integer'}], 'description': 'Implementation of the Cobweb clustering algorithm. For more information see:\nD. Fisher (1987). Knowledge acquisition via incremental conceptual clustering. Machine Learning. 2(2):139-172. and J. H. Gennari, P. Langley, D. Fisher (1990). Models of incremental concept formation. Artificial Intelligence. 40:11-61.', 'returns': 'Clusterer', 'type': 'Algorithm', 'hidden': False, 'name': 'Clusterer.wekaCobweb'})
# Clusterer.wekaKMeans
# Cluster data using the k means algorithm. Can use either the Euclidean
# distance (default) or the Manhattan distance. If the Manhattan distance is
# used, then centroids are computed as the component-wise median rather than
# mean. For more information see: D. Arthur, S. Vassilvitskii: k-means++: the
# advantages of carefull seeding. In: Proceedings of the eighteenth annual
# ACM-SIAM symposium on Discrete algorithms, 1027-1035, 2007.
#
# Args:
#   nClusters: Number of clusters.
#   init: Initialization method to use.0 = random, 1 = k-means++, 2 =
#       canopy, 3 = farthest first.
#   canopies: Use canopies to reduce the number of distance
#       calculations.
#   maxCandidates: Maximum number of candidate canopies to
#       retain in memory at any one time when using canopy
#       clustering. T2 distance plus, data characteristics,
#       will determine how many candidate canopies are
#       formed before periodic and final pruning are
#       performed, which might result in exceess memory
#       consumption. This setting avoids large numbers of
#       candidate canopies consuming memory.
#   periodicPruning: How often to prune low density
#       canopies when using canopy clustering.
#   minDensity: Minimum canopy density, when using canopy
#       clustering, below which a canopy will be pruned during
#       periodic pruning.
#   t1: The T1 distance to use when using canopy clustering. A value <
#       0 is taken as a positive multiplier for T2.
#   t2: The T2 distance to use when using canopy clustering. Values < 0
#       cause a heuristic based on attribute std. deviation to be used.
#   distanceFunction: Distance function to use.  Options
#       are: Euclidean & Manhattan
#   maxIterations: Maximum number of iterations.
#   preserveOrder: Preserve order of instances.
#   fast: Enables faster distance calculations, using cut-off values.
#       Disables the calculation/output of squared errors/distances
#   seed: The randomization seed.
signatures.append({'args': [{'description': 'Number of clusters.', 'name': 'nClusters', 'type': 'Integer'}, {'default': 0, 'description': 'Initialization method to use.0 = random, 1 = k-means++, 2 = canopy, 3 = farthest first.', 'name': 'init', 'optional': True, 'type': 'Integer'}, {'default': False, 'description': 'Use canopies to reduce the number of distance calculations.', 'name': 'canopies', 'optional': True, 'type': 'Boolean'}, {'default': 100, 'description': 'Maximum number of candidate canopies to retain in memory at any one time when using canopy clustering. T2 distance plus, data characteristics, will determine how many candidate canopies are formed before periodic and final pruning are performed, which might result in exceess memory consumption. This setting avoids large numbers of candidate canopies consuming memory.', 'name': 'maxCandidates', 'optional': True, 'type': 'Integer'}, {'default': 10000, 'description': 'How often to prune low density canopies when using canopy clustering.', 'name': 'periodicPruning', 'optional': True, 'type': 'Integer'}, {'default': 2, 'description': 'Minimum canopy density, when using canopy clustering, below which a canopy will be pruned during periodic pruning.', 'name': 'minDensity', 'optional': True, 'type': 'Integer'}, {'default': -1.5, 'description': 'The T1 distance to use when using canopy clustering. A value < 0 is taken as a positive multiplier for T2.', 'name': 't1', 'optional': True, 'type': 'Float'}, {'default': -1.0, 'description': 'The T2 distance to use when using canopy clustering. Values < 0 cause a heuristic based on attribute std. deviation to be used.', 'name': 't2', 'optional': True, 'type': 'Float'}, {'default': 'Euclidean', 'description': 'Distance function to use.  Options are: Euclidean & Manhattan', 'name': 'distanceFunction', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'Maximum number of iterations.', 'name': 'maxIterations', 'optional': True, 'type': 'Integer'}, {'default': False, 'description': 'Preserve order of instances.', 'name': 'preserveOrder', 'optional': True, 'type': 'Boolean'}, {'default': False, 'description': 'Enables faster distance calculations, using cut-off values. Disables the calculation/output of squared errors/distances', 'name': 'fast', 'optional': True, 'type': 'Boolean'}, {'default': 10, 'description': 'The randomization seed.', 'name': 'seed', 'optional': True, 'type': 'Integer'}], 'description': 'Cluster data using the k means algorithm. Can use either the Euclidean distance (default) or the Manhattan distance. If the Manhattan distance is used, then centroids are computed as the component-wise median rather than mean. For more information see:\nD. Arthur, S. Vassilvitskii: k-means++: the advantages of carefull seeding. In: Proceedings of the eighteenth annual ACM-SIAM symposium on Discrete algorithms, 1027-1035, 2007.', 'returns': 'Clusterer', 'type': 'Algorithm', 'hidden': False, 'name': 'Clusterer.wekaKMeans'})
# Clusterer.wekaLVQ
# A Clusterer that implements the Learning Vector Quantization algorithm. For
# more details, see: T. Kohonen, "Learning Vector Quantization", The Handbook
# of Brain Theory and Neural Networks, 2nd Edition, MIT Press, 2003, pp.
# 631-634.
#
# Args:
#   numClusters: The number of clusters.
#   learningRate: The learning rate for the training
#       algorithm. (Value should be greaterthan 0 and less or
#       equal to 1).
#   epochs: Number of training epochs. (Value should be greater
#       than or equal to 1).
#   normalizeInput: Skip normalizing the attributes.
signatures.append({'args': [{'default': 7, 'description': 'The number of clusters.', 'name': 'numClusters', 'optional': True, 'type': 'Integer'}, {'default': 1.0, 'description': 'The learning rate for the training algorithm. (Value should be greaterthan 0 and less or equal to 1).', 'name': 'learningRate', 'optional': True, 'type': 'Float'}, {'default': 1000, 'description': 'Number of training epochs. (Value should be greater than or equal to 1).', 'name': 'epochs', 'optional': True, 'type': 'Integer'}, {'default': False, 'description': 'Skip normalizing the attributes.', 'name': 'normalizeInput', 'optional': True, 'type': 'Boolean'}], 'description': 'A Clusterer that implements the Learning Vector Quantization algorithm. For more details, see:\nT. Kohonen, "Learning Vector Quantization", The Handbook of Brain Theory and Neural Networks, 2nd Edition, MIT Press, 2003, pp. 631-634.', 'returns': 'Clusterer', 'type': 'Algorithm', 'hidden': False, 'name': 'Clusterer.wekaLVQ'})
# Clusterer.wekaXMeans
# X-Means is K-Means with an efficient estimation of the number of clusters.
# For more information see: Dan Pelleg, Andrew W. Moore: X-means: Extending
# K-means with Efficient Estimation of the Number of Clusters. In:
# Seventeenth International Conference on Machine Learning, 727-734, 2000.
#
# Args:
#   minClusters: Minimum number of clusters.
#   maxClusters: Maximum number of clusters.
#   maxIterations: Maximum number of overall iterations.
#   maxKMeans: The maximum number of iterations to perform in
#       KMeans.
#   maxForChildren: The maximum number of iterations in
#       KMeans that is performed on the child centers.
#   useKD: Use a KDTree.
#   cutoffFactor: Takes the given percentage of the splitted
#       centroids if none of the children win.
#   distanceFunction: Distance function to use.  Options
#       are: Chebyshev, Euclidean & Manhattan.
#   seed: The randomization seed.
signatures.append({'args': [{'default': 2, 'description': 'Minimum number of clusters.', 'name': 'minClusters', 'optional': True, 'type': 'Integer'}, {'default': 8, 'description': 'Maximum number of clusters.', 'name': 'maxClusters', 'optional': True, 'type': 'Integer'}, {'default': 3, 'description': 'Maximum number of overall iterations.', 'name': 'maxIterations', 'optional': True, 'type': 'Integer'}, {'default': 1000, 'description': 'The maximum number of iterations to perform in KMeans.', 'name': 'maxKMeans', 'optional': True, 'type': 'Integer'}, {'default': 1000, 'description': 'The maximum number of iterations in KMeans that is performed on the child centers.', 'name': 'maxForChildren', 'optional': True, 'type': 'Integer'}, {'default': False, 'description': 'Use a KDTree.', 'name': 'useKD', 'optional': True, 'type': 'Boolean'}, {'default': 0.0, 'description': 'Takes the given percentage of the splitted centroids if none of the children win.', 'name': 'cutoffFactor', 'optional': True, 'type': 'Float'}, {'default': 'Euclidean', 'description': 'Distance function to use.  Options are: Chebyshev, Euclidean & Manhattan.', 'name': 'distanceFunction', 'optional': True, 'type': 'String'}, {'default': 10, 'description': 'The randomization seed.', 'name': 'seed', 'optional': True, 'type': 'Integer'}], 'description': 'X-Means is K-Means with an efficient estimation of the number of clusters. For more information see:\nDan Pelleg, Andrew W. Moore: X-means: Extending K-means with Efficient Estimation of the Number of Clusters. In: Seventeenth International Conference on Machine Learning, 727-734, 2000.', 'returns': 'Clusterer', 'type': 'Algorithm', 'hidden': False, 'name': 'Clusterer.wekaXMeans'})
# Collection
# Returns a Collection containing the specified features.
#
# Args:
#   features: The features comprising the collection.
signatures.append({'args': [{'description': 'The features comprising the collection.', 'name': 'features', 'type': 'List'}], 'description': 'Returns a Collection containing the specified features.', 'returns': 'FeatureCollection', 'type': 'Algorithm', 'hidden': False, 'name': 'Collection'})
# Collection.cache
# Caches the given collection.
#
# Args:
#   collection: The collection to cache.
signatures.append({'args': [{'description': 'The collection to cache.', 'name': 'collection', 'type': 'FeatureCollection'}], 'description': 'Caches the given collection.', 'returns': 'FeatureCollection', 'type': 'Algorithm', 'hidden': True, 'name': 'Collection.cache'})
# Collection.distance
# Produces a DOUBLE image where each pixel is the distance in meters from the
# pixel center to the nearest part of any Point or LineString features in the
# collection. Pixels that are not within 'searchRadius' meters of a geometry
# will be masked out. Distances are computed on a sphere, so there is a small
# error proportional to the latitude difference between each pixel and the
# nearest geometry.
#
# Args:
#   features: Feature collection from which to get features used
#       to compute pixel distances.
#   searchRadius: Maximum distance in meters from each pixel
#       to look for edges. Pixels will be masked unless there
#       are edges within this distance.
#   maxError: Maximum reprojection error in meters, only used if
#       the input polylines require reprojection. If '0' is
#       provided, then this operation will fail if projection is
#       required.
signatures.append({'args': [{'description': 'Feature collection from which to get features used to compute pixel distances.', 'name': 'features', 'type': 'FeatureCollection'}, {'default': 100000.0, 'description': 'Maximum distance in meters from each pixel to look for edges. Pixels will be masked unless there are edges within this distance.', 'name': 'searchRadius', 'optional': True, 'type': 'Float'}, {'default': 100.0, 'description': "Maximum reprojection error in meters, only used if the input polylines require reprojection. If '0' is provided, then this operation will fail if projection is required.", 'name': 'maxError', 'optional': True, 'type': 'Float'}], 'description': "Produces a DOUBLE image where each pixel is the distance in meters from the pixel center to the nearest part of any Point or LineString features in the collection. Pixels that are not within 'searchRadius' meters of a geometry will be masked out.\nDistances are computed on a sphere, so there is a small error proportional to the latitude difference between each pixel and the nearest geometry.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Collection.distance'})
# Collection.distinct
# Removes duplicates from a collection. Note that duplicates are determined
# using a strong hash over the serialized form of the selected properties.
#
# Args:
#   collection: The input collection from which objects will be
#       selected.
#   selectors: Which parts of the object to use for comparisons.
signatures.append({'args': [{'description': 'The input collection from which objects will be selected.', 'name': 'collection', 'type': 'FeatureCollection'}, {'description': 'Which parts of the object to use for comparisons.', 'name': 'selectors', 'type': 'SelectorSet'}], 'description': 'Removes duplicates from a collection. Note that duplicates are determined using a strong hash over the serialized form of the selected properties.', 'returns': 'FeatureCollection', 'type': 'Algorithm', 'hidden': False, 'name': 'Collection.distinct'})
# Collection.draw
# Paints a vector collection for visualization. Not intended for use as input
# to other algorithms.
#
# Args:
#   collection: The collection to draw.
#   color: A hex string in the format RRGGBB specifying the color to
#       use for drawing the features.
#   pointRadius: The radius in pixels of the point markers.
#   strokeWidth: The width in pixels of lines and polygon
#       borders.
signatures.append({'args': [{'description': 'The collection to draw.', 'name': 'collection', 'type': 'FeatureCollection'}, {'description': 'A hex string in the format RRGGBB specifying the color to use for drawing the features.', 'name': 'color', 'type': 'String'}, {'default': 3, 'description': 'The radius in pixels of the point markers.', 'name': 'pointRadius', 'optional': True, 'type': 'Integer'}, {'default': 2, 'description': 'The width in pixels of lines and polygon borders.', 'name': 'strokeWidth', 'optional': True, 'type': 'Integer'}], 'description': 'Paints a vector collection for visualization. Not intended for use as input to other algorithms.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Collection.draw'})
# Collection.errorMatrix
# Computes a 2D error matrix for a collection by comparing two columns of a
# collection: one containing the actual values, and one containing predicted
# values.The values are expected to be small contiguous integers, starting
# from 0. Axis 0 (the rows) of the matrix correspond to the actual values,
# and Axis 1 (the columns) to the predicted values.
#
# Args:
#   collection: The input collection.
#   actual: The name of the property containing the actual value.
#   predicted: The name of the property containing the predicted
#       value.
#   order: A list of the expected values.  If this argument is not
#       specified, the values are assumed to be contiguous and span
#       the range 0 to maxValue. If specified, only values matching
#       this list are used, and the matrix will have dimensions and
#       order matching the this list.
signatures.append({'args': [{'description': 'The input collection.', 'name': 'collection', 'type': 'FeatureCollection'}, {'description': 'The name of the property containing the actual value.', 'name': 'actual', 'type': 'String'}, {'description': 'The name of the property containing the predicted value.', 'name': 'predicted', 'type': 'String'}, {'default': None, 'description': 'A list of the expected values.  If this argument is not specified, the values are assumed to be contiguous and span the range 0 to maxValue. If specified, only values matching this list are used, and the matrix will have dimensions and order matching the this list.', 'name': 'order', 'optional': True, 'type': 'List'}], 'description': 'Computes a 2D error matrix for a collection by comparing two columns of a collection: one containing the actual values, and one containing predicted values.The values are expected to be small contiguous integers, starting from 0. Axis 0 (the rows) of the matrix correspond to the actual values, and Axis 1 (the columns) to the predicted values.', 'returns': 'ConfusionMatrix', 'type': 'Algorithm', 'hidden': False, 'name': 'Collection.errorMatrix'})
# Collection.filter
# Applies a filter to a given collection.
#
# Args:
#   collection: The collection to filter.
#   filter: The filter to apply.
signatures.append({'args': [{'description': 'The collection to filter.', 'name': 'collection', 'type': 'FeatureCollection'}, {'description': 'The filter to apply.', 'name': 'filter', 'type': 'Filter'}], 'description': 'Applies a filter to a given collection.', 'returns': 'FeatureCollection', 'type': 'Algorithm', 'hidden': False, 'name': 'Collection.filter'})
# Collection.first
# Returns the first entry from a given collection.
#
# Args:
#   collection: The collection from which to select the first
#       entry.
signatures.append({'args': [{'description': 'The collection from which to select the first entry.', 'name': 'collection', 'type': 'FeatureCollection'}], 'description': 'Returns the first entry from a given collection.', 'returns': 'Element', 'type': 'Algorithm', 'hidden': False, 'name': 'Collection.first'})
# Collection.flatten
# Flattens collections of collections.
#
# Args:
#   collection: The input collection of collections.
signatures.append({'args': [{'description': 'The input collection of collections.', 'name': 'collection', 'type': 'FeatureCollection'}], 'description': 'Flattens collections of collections.', 'returns': 'FeatureCollection', 'type': 'Algorithm', 'hidden': False, 'name': 'Collection.flatten'})
# Collection.fromColumns
# Creates a FeatureCollection, given a list of values for each property.
#
# Args:
#   columns: A list of values for each property; must have the
#       same length as propertyNames.
#   propertyNames: The property names for features in this
#       collection.
#   propertyTypes: The type of each property; if present,
#       must have the same length as propertyNames.
signatures.append({'args': [{'description': 'A list of values for each property; must have the same length as propertyNames.', 'name': 'columns', 'type': 'List'}, {'description': 'The property names for features in this collection.', 'name': 'propertyNames', 'type': 'List'}, {'default': None, 'description': 'The type of each property; if present, must have the same length as propertyNames.', 'name': 'propertyTypes', 'optional': True, 'type': 'List'}], 'description': 'Creates a FeatureCollection, given a list of values for each property.', 'returns': 'FeatureCollection', 'type': 'Algorithm', 'hidden': True, 'name': 'Collection.fromColumns'})
# Collection.geometry
# Extracts and merges the geometries of a collection. Requires that all the
# geometries in the collection share the projection and edge interpretation.
#
# Args:
#   collection: The collection whose geometries will be
#       extracted.
#   maxError: An error margin to use when merging geometries.
signatures.append({'args': [{'description': 'The collection whose geometries will be extracted.', 'name': 'collection', 'type': 'FeatureCollection'}, {'default': {'type': 'ErrorMargin', 'unit': 'meters', 'value': 0.0}, 'description': 'An error margin to use when merging geometries.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}], 'description': 'Extracts and merges the geometries of a collection. Requires that all the geometries in the collection share the projection and edge interpretation.', 'returns': 'Geometry', 'type': 'Algorithm', 'hidden': False, 'name': 'Collection.geometry'})
# Collection.iterate
# Applies a user-supplied function to each element of a collection. The user-
# supplied function is given two arguments: the current element, and the
# value returned by the previous call to iterate() or the first argument, for
# the first iteration.  The result is the value returned by the final call to
# the user-supplied function.
#
# Args:
#   collection: The collection to which the algorithm is
#       applied.
#   function: The function to apply to each element.  Must take
#       two arguments: an element of the collection and the value
#       from the previous iteration.
#   first: The initial state.
signatures.append({'args': [{'description': 'The collection to which the algorithm is applied.', 'name': 'collection', 'type': 'FeatureCollection'}, {'description': 'The function to apply to each element.  Must take two arguments: an element of the collection and the value from the previous iteration.', 'name': 'function', 'type': 'Algorithm'}, {'default': None, 'description': 'The initial state.', 'name': 'first', 'optional': True, 'type': 'Object'}], 'description': 'Applies a user-supplied function to each element of a collection. The user-supplied function is given two arguments: the current element, and the value returned by the previous call to iterate() or the first argument, for the first iteration.  The result is the value returned by the final call to the user-supplied function.', 'returns': 'Object', 'type': 'Algorithm', 'hidden': False, 'name': 'Collection.iterate'})
# Collection.limit
# Applies an ordering and limit to a given collection.
#
# Args:
#   collection: The collection to limit or order.
#   limit: The maximum number of items in the output collection.
#       null is used to represent no limit.
#   key: The property on which the collection is sorted.
#   ascending: Whether the sorting is ascending rather than
#       descending.
signatures.append({'args': [{'description': 'The collection to limit or order.', 'name': 'collection', 'type': 'FeatureCollection'}, {'default': None, 'description': 'The maximum number of items in the output collection. null is used to represent no limit.', 'name': 'limit', 'optional': True, 'type': 'Integer'}, {'default': None, 'description': 'The property on which the collection is sorted.', 'name': 'key', 'optional': True, 'type': 'String'}, {'default': True, 'description': 'Whether the sorting is ascending rather than descending.', 'name': 'ascending', 'optional': True, 'type': 'Boolean'}], 'description': 'Applies an ordering and limit to a given collection.', 'returns': 'FeatureCollection', 'type': 'Algorithm', 'hidden': False, 'name': 'Collection.limit'})
# Collection.loadTable
# Returns a Collection of features from a specified table.
#
# Args:
#   tableId: The ID of the table to load. Either an asset ID or a
#       Fusion Table DocID prefixed with 'ft:'.
#   geometryColumn: The name of the column to use as the
#       main feature geometry. Not used if tableId is an
#       asset ID.
#   version: The version of the asset. -1 signifies the latest
#       version. Ignored unless tableId is an asset ID.
signatures.append({'args': [{'description': "The ID of the table to load. Either an asset ID or a Fusion Table DocID prefixed with 'ft:'.", 'name': 'tableId', 'type': 'Object'}, {'default': None, 'description': 'The name of the column to use as the main feature geometry. Not used if tableId is an asset ID.', 'name': 'geometryColumn', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The version of the asset. -1 signifies the latest version. Ignored unless tableId is an asset ID.', 'name': 'version', 'optional': True, 'type': 'Long'}], 'description': 'Returns a Collection of features from a specified table.', 'returns': 'FeatureCollection', 'type': 'Algorithm', 'hidden': False, 'name': 'Collection.loadTable'})
# Collection.map
# Maps an algorithm over a collection.
#
# Args:
#   collection: The collection of the elements to which the
#       algorithm is applied.
#   baseAlgorithm: The algorithm being applied to each
#       element.
#   dropNulls: If true, the mapped algorithm is allowed to
#       return nulls, and the elements for which it returns
#       nulls will be dropped.
signatures.append({'args': [{'description': 'The collection of the elements to which the algorithm is applied.', 'name': 'collection', 'type': 'FeatureCollection'}, {'description': 'The algorithm being applied to each element.', 'name': 'baseAlgorithm', 'type': 'Algorithm'}, {'default': False, 'description': 'If true, the mapped algorithm is allowed to return nulls, and the elements for which it returns nulls will be dropped.', 'name': 'dropNulls', 'optional': True, 'type': 'Boolean'}], 'description': 'Maps an algorithm over a collection.', 'returns': 'FeatureCollection', 'type': 'Algorithm', 'hidden': False, 'name': 'Collection.map'})
# Collection.merge
# Merges two collections into one. The result has all the elements that were
# in either collection.
#
# Args:
#   collection1: The first collection to merge.
#   collection2: The second collection to merge.
signatures.append({'args': [{'description': 'The first collection to merge.', 'name': 'collection1', 'type': 'FeatureCollection'}, {'description': 'The second collection to merge.', 'name': 'collection2', 'type': 'FeatureCollection'}], 'description': 'Merges two collections into one. The result has all the elements that were in either collection.', 'returns': 'FeatureCollection', 'type': 'Algorithm', 'hidden': False, 'name': 'Collection.merge'})
# Collection.randomColumn
# Adds a column of deterministic pseudorandom numbers to a collection.  The
# numbers are double-precision floating point numbers in the range 0.0
# (inclusive) to 1.0 (exclusive).
#
# Args:
#   collection: The input collection to which to add a random
#       column.
#   columnName: The name of the column to add.
#   seed: A seed used when generating the random numbers.
signatures.append({'args': [{'description': 'The input collection to which to add a random column.', 'name': 'collection', 'type': 'FeatureCollection'}, {'default': 'random', 'description': 'The name of the column to add.', 'name': 'columnName', 'optional': True, 'type': 'String'}, {'default': 0, 'description': 'A seed used when generating the random numbers.', 'name': 'seed', 'optional': True, 'type': 'Long'}], 'description': 'Adds a column of deterministic pseudorandom numbers to a collection.  The numbers are double-precision floating point numbers in the range 0.0 (inclusive) to 1.0 (exclusive).', 'returns': 'FeatureCollection', 'type': 'Algorithm', 'hidden': False, 'name': 'Collection.randomColumn'})
# Collection.reduceColumns
# Apply a reducer to each element of a collection, using the given selectors
# to determine the inputs. Returns a dictionary of results, keyed with the
# output names.
#
# Args:
#   collection: The collection to aggregate over.
#   reducer: The reducer to apply.
#   selectors: A selector for each input of the reducer.
#   weightSelectors: A selector for each weighted input of
#       the reducer.
signatures.append({'args': [{'description': 'The collection to aggregate over.', 'name': 'collection', 'type': 'FeatureCollection'}, {'description': 'The reducer to apply.', 'name': 'reducer', 'type': 'Reducer'}, {'description': 'A selector for each input of the reducer.', 'name': 'selectors', 'type': 'List'}, {'default': None, 'description': 'A selector for each weighted input of the reducer.', 'name': 'weightSelectors', 'optional': True, 'type': 'List'}], 'description': 'Apply a reducer to each element of a collection, using the given selectors to determine the inputs.\nReturns a dictionary of results, keyed with the output names.', 'returns': 'Dictionary', 'type': 'Algorithm', 'hidden': False, 'name': 'Collection.reduceColumns'})
# Collection.reduceToImage
# Creates an image from a feature collection by applying a reducer over the
# selected properties of all the features that intersect each pixel.
#
# Args:
#   collection: Feature collection to intersect with each
#       output pixel.
#   properties: Properties to select from each feature and pass
#       into the reducer.
#   reducer: A Reducer to combine the properties of each
#       intersecting feature into a final result to store in the
#       pixel.
signatures.append({'args': [{'description': 'Feature collection to intersect with each output pixel.', 'name': 'collection', 'type': 'FeatureCollection'}, {'description': 'Properties to select from each feature and pass into the reducer.', 'name': 'properties', 'type': 'List'}, {'description': 'A Reducer to combine the properties of each intersecting feature into a final result to store in the pixel.', 'name': 'reducer', 'type': 'Reducer'}], 'description': 'Creates an image from a feature collection by applying a reducer over the selected properties of all the features that intersect each pixel.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Collection.reduceToImage'})
# Collection.remap
# Remaps the value of a specific property in a collection. Takes two parallel
# lists and maps values found in one to values in the other. Any element with
# a value that is not specified in the first list is dropped from the output
# collection.
#
# Args:
#   collection: The collection to be modified.
#   lookupIn: The input mapping values. Restricted to strings and
#       integers.
#   lookupOut: The output mapping values. Must be the same size
#       as lookupIn.
#   columnName: The name of the property to remap.
signatures.append({'args': [{'description': 'The collection to be modified.', 'name': 'collection', 'type': 'FeatureCollection'}, {'description': 'The input mapping values. Restricted to strings and integers.', 'name': 'lookupIn', 'type': 'List'}, {'description': 'The output mapping values. Must be the same size as lookupIn.', 'name': 'lookupOut', 'type': 'List'}, {'description': 'The name of the property to remap.', 'name': 'columnName', 'type': 'String'}], 'description': 'Remaps the value of a specific property in a collection. Takes two parallel lists and maps values found in one to values in the other. Any element with a value that is not specified in the first list is dropped from the output collection.', 'returns': 'FeatureCollection', 'type': 'Algorithm', 'hidden': False, 'name': 'Collection.remap'})
# Collection.size
# Returns the number of elements in the collection.
#
# Args:
#   collection: The collection to count.
signatures.append({'args': [{'description': 'The collection to count.', 'name': 'collection', 'type': 'FeatureCollection'}], 'description': 'Returns the number of elements in the collection.', 'returns': 'Integer', 'type': 'Algorithm', 'hidden': False, 'name': 'Collection.size'})
# Collection.style
# Draw a vector collection for visualization using a simple style language.
#
# Args:
#   collection: The collection to draw.
#   color: A default color (CSS 3.0 color value e.g. 'FF0000' or
#       'red') to use for drawing the features.  Supports opacity
#       (e.g.: 'FF000088' for 50% transparent red).
#   pointSize: The default size in pixels of the point markers.
#   pointShape: The default shape of the marker to draw at each
#       point location.  One of: circle, square, diamond,
#       cross, plus, pentagram, hexagram, triangle, triangle_up
#       triangle_down, triangle_left, triangle_right, pentagon,
#       hexagon, star5, star6. This argument also supports the
#       following Matlab marker abbreviations: o, s, d, x, +,
#       p, h, ^, v, <, >.
#   width: The default line width for lines and outlines for
#       polygons and point shapes.
#   fillColor: The color for filling polygons and point shapes.
#       Defaults to 'color' at 0.66 opacity.
#   styleProperty: A per-feature property expected to
#       contain a dictionary. Values in the dictionary
#       override any default values for that feature.
#   neighborhood: If styleProperty is used and any feature
#       has a pointSize or width larger than the defaults,
#       tiling artifacts can occur. Specifies the maximum
#       neighborhood (pointSize + width) needed for any
#       feature.
signatures.append({'args': [{'description': 'The collection to draw.', 'name': 'collection', 'type': 'FeatureCollection'}, {'default': 'black', 'description': "A default color (CSS 3.0 color value e.g. 'FF0000' or 'red') to use for drawing the features.  Supports opacity (e.g.: 'FF000088' for 50% transparent red).", 'name': 'color', 'optional': True, 'type': 'String'}, {'default': 3, 'description': 'The default size in pixels of the point markers.', 'name': 'pointSize', 'optional': True, 'type': 'Integer'}, {'default': 'circle', 'description': 'The default shape of the marker to draw at each point location.  One of: circle, square, diamond, cross, plus, pentagram, hexagram, triangle, triangle_up triangle_down, triangle_left, triangle_right, pentagon, hexagon, star5, star6. This argument also supports the following Matlab marker abbreviations: o, s, d, x, +, p, h, ^, v, <, >.', 'name': 'pointShape', 'optional': True, 'type': 'String'}, {'default': 2.0, 'description': 'The default line width for lines and outlines for polygons and point shapes.', 'name': 'width', 'optional': True, 'type': 'Float'}, {'default': None, 'description': "The color for filling polygons and point shapes.  Defaults to 'color' at 0.66 opacity.", 'name': 'fillColor', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'A per-feature property expected to contain a dictionary. Values in the dictionary override any default values for that feature.', 'name': 'styleProperty', 'optional': True, 'type': 'String'}, {'default': 5, 'description': 'If styleProperty is used and any feature has a pointSize or width larger than the defaults, tiling artifacts can occur. Specifies the maximum neighborhood (pointSize + width) needed for any feature.', 'name': 'neighborhood', 'optional': True, 'type': 'Integer'}], 'description': 'Draw a vector collection for visualization using a simple style language.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Collection.style'})
# Collection.toList
# Returns the elements of a collection as a list.
#
# Args:
#   collection: The input collection to fetch.
#   count: The maximum number of elements to fetch.
#   offset: The number of elements to discard from the start. If
#       set, (offset + count) elements will be fetched and the
#       first offset elements will be discarded.
signatures.append({'args': [{'description': 'The input collection to fetch.', 'name': 'collection', 'type': 'FeatureCollection'}, {'description': 'The maximum number of elements to fetch.', 'name': 'count', 'type': 'Integer'}, {'default': 0, 'description': 'The number of elements to discard from the start. If set, (offset + count) elements will be fetched and the first offset elements will be discarded.', 'name': 'offset', 'optional': True, 'type': 'Integer'}], 'description': 'Returns the elements of a collection as a list.', 'returns': 'List', 'type': 'Algorithm', 'hidden': False, 'name': 'Collection.toList'})
# Collection.union
# Merges all geometries in a given collection into one and returns a
# collection containing a single feature with only an ID of 'union_result'
# and a geometry.
#
# Args:
#   collection: The collection being merged.
#   maxError: The maximum error allowed when performing any
#       necessary reprojections. If not specified, defaults to
#       the error margin requested from the output.
signatures.append({'args': [{'description': 'The collection being merged.', 'name': 'collection', 'type': 'FeatureCollection'}, {'default': None, 'description': 'The maximum error allowed when performing any necessary reprojections. If not specified, defaults to the error margin requested from the output.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}], 'description': "Merges all geometries in a given collection into one and returns a collection containing a single feature with only an ID of 'union_result' and a geometry.", 'returns': 'FeatureCollection', 'type': 'Algorithm', 'hidden': False, 'name': 'Collection.union'})
# ConfusionMatrix
# Creates a confusion matrix. Axis 1 (the rows) of the matrix correspond to
# the actual values, and Axis 0 (the columns) to the predicted values.
#
# Args:
#   array: A square, 2D array of integers, representing the
#       confusion matrix.
#   order: The row and column size and order, for non-contiguous or
#       non-zero based matrices.
signatures.append({'args': [{'description': 'A square, 2D array of integers, representing the confusion matrix.', 'name': 'array', 'type': 'Object'}, {'default': None, 'description': 'The row and column size and order, for non-contiguous or non-zero based matrices.', 'name': 'order', 'optional': True, 'type': 'List'}], 'description': 'Creates a confusion matrix. Axis 1 (the rows) of the matrix correspond to the actual values, and Axis 0 (the columns) to the predicted values.', 'returns': 'ConfusionMatrix', 'type': 'Algorithm', 'hidden': False, 'name': 'ConfusionMatrix'})
# ConfusionMatrix.accuracy
# Computes the overall accuracy of a confusion matrix defined as correct /
# total.
#
# Args:
#   confusionMatrix
signatures.append({'args': [{'name': 'confusionMatrix', 'type': 'ConfusionMatrix'}], 'description': 'Computes the overall accuracy of a confusion matrix defined as correct / total.', 'returns': 'Float', 'type': 'Algorithm', 'hidden': False, 'name': 'ConfusionMatrix.accuracy'})
# ConfusionMatrix.array
# Returns a confusion matrix as an Array.
#
# Args:
#   confusionMatrix
signatures.append({'args': [{'name': 'confusionMatrix', 'type': 'ConfusionMatrix'}], 'description': 'Returns a confusion matrix as an Array.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'ConfusionMatrix.array'})
# ConfusionMatrix.consumersAccuracy
# Computes the consumer's accuracy (reliability) of a confusion matrix
# defined as (correct / total) for each row.
#
# Args:
#   confusionMatrix
signatures.append({'args': [{'name': 'confusionMatrix', 'type': 'ConfusionMatrix'}], 'description': "Computes the consumer's accuracy (reliability) of a confusion matrix defined as (correct / total) for each row.", 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'ConfusionMatrix.consumersAccuracy'})
# ConfusionMatrix.kappa
# Computes the Kappa statistic for the confusion matrix.
#
# Args:
#   confusionMatrix
signatures.append({'args': [{'name': 'confusionMatrix', 'type': 'ConfusionMatrix'}], 'description': 'Computes the Kappa statistic for the confusion matrix.', 'returns': 'Float', 'type': 'Algorithm', 'hidden': False, 'name': 'ConfusionMatrix.kappa'})
# ConfusionMatrix.order
# Returns the name and order of the rows and columns of the matrix.
#
# Args:
#   confusionMatrix
signatures.append({'args': [{'name': 'confusionMatrix', 'type': 'ConfusionMatrix'}], 'description': 'Returns the name and order of the rows and columns of the matrix.', 'returns': 'List', 'type': 'Algorithm', 'hidden': False, 'name': 'ConfusionMatrix.order'})
# ConfusionMatrix.producersAccuracy
# Computes the producer's accuracy of a confusion matrix defined as (correct
# / total) for each column.
#
# Args:
#   confusionMatrix
signatures.append({'args': [{'name': 'confusionMatrix', 'type': 'ConfusionMatrix'}], 'description': "Computes the producer's accuracy of a confusion matrix defined as (correct / total) for each column.", 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'ConfusionMatrix.producersAccuracy'})
# CrossCorrelation
# Gives information on the quality of image registration between two
# (theoretically) co-registered images. The input is two images with the same
# number of bands. This function outputs an image composed of four bands of
# information. The first three are distances: the deltaX, deltaY, and the
# Euclidean distance for each pixel in imageA to the pixel which has the
# highest corresponding correlation coefficient in imageB. The fourth band is
# the value of the correlation coefficient for that pixel [-1 : +1].
#
# Args:
#   imageA: First image, with N bands.
#   imageB: Second image, must have the same number of bands as
#       imageA.
#   maxGap: The greatest distance a pixel may shift in either X or
#       Y.
#   windowSize: Size of the window to be compared.
#   maxMaskedFrac: The maximum fraction of pixels within the
#       correlation window that are allowed to be masked.
#       This test is applied at each offset location within
#       the search region. For each offset, the overlapping
#       image patches are compared and a correlation score
#       computed. A pixel within these overlapping patches
#       is considered masked if either of the patches is
#       masked there. If the test fails at any single
#       location in the search region, the ouput pixel for
#       which the correlation is being computed is
#       considered invalid, and will be masked.
signatures.append({'args': [{'description': 'First image, with N bands.', 'name': 'imageA', 'type': 'Image'}, {'description': 'Second image, must have the same number of bands as imageA.', 'name': 'imageB', 'type': 'Image'}, {'description': 'The greatest distance a pixel may shift in either X or Y.', 'name': 'maxGap', 'type': 'Integer'}, {'description': 'Size of the window to be compared.', 'name': 'windowSize', 'type': 'Integer'}, {'default': 0.0, 'description': 'The maximum fraction of pixels within the correlation window that are allowed to be masked. This test is applied at each offset location within the search region. For each offset, the overlapping image patches are compared and a correlation score computed. A pixel within these overlapping patches is considered masked if either of the patches is masked there. If the test fails at any single location in the search region, the ouput pixel for which the correlation is being computed is considered invalid, and will be masked.', 'name': 'maxMaskedFrac', 'optional': True, 'type': 'Float'}], 'description': 'Gives information on the quality of image registration between two (theoretically) co-registered images. The input is two images with the same number of bands. This function outputs an image composed of four bands of information. The first three are distances: the deltaX, deltaY, and the Euclidean distance for each pixel in imageA to the pixel which has the highest corresponding correlation coefficient in imageB. The fourth band is the value of the correlation coefficient for that pixel [-1 : +1].', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'CrossCorrelation'})
# Date
# Creates a Date.
#
# Args:
#   value: A number (interpreted as milliseconds since
#       1970-01-01T00:00:00Z), or string such as '1996-01-01' or
#       '1996-001' or '1996-01-01T08:00'.
#   timeZone: The time zone (e.g. 'America/Los_Angeles');
#       defaults to UTC.
signatures.append({'args': [{'description': "A number (interpreted as milliseconds since 1970-01-01T00:00:00Z), or string such as '1996-01-01' or '1996-001' or '1996-01-01T08:00'.", 'name': 'value', 'type': 'Object'}, {'default': None, 'description': "The time zone (e.g. 'America/Los_Angeles'); defaults to UTC.", 'name': 'timeZone', 'optional': True, 'type': 'String'}], 'description': 'Creates a Date.', 'returns': 'Date', 'type': 'Algorithm', 'hidden': False, 'name': 'Date'})
# Date.advance
# Create a new Date by adding the specified units to the given Date.
#
# Args:
#   date
#   delta
#   unit: One of 'year', 'month' 'week', 'day', 'hour', 'minute', or
#       'second'.
#   timeZone: The time zone (e.g. 'America/Los_Angeles');
#       defaults to UTC.
signatures.append({'args': [{'name': 'date', 'type': 'Date'}, {'name': 'delta', 'type': 'Float'}, {'description': "One of 'year', 'month' 'week', 'day', 'hour', 'minute', or 'second'.", 'name': 'unit', 'type': 'String'}, {'default': None, 'description': "The time zone (e.g. 'America/Los_Angeles'); defaults to UTC.", 'name': 'timeZone', 'optional': True, 'type': 'String'}], 'description': 'Create a new Date by adding the specified units to the given Date.', 'returns': 'Date', 'type': 'Algorithm', 'hidden': False, 'name': 'Date.advance'})
# Date.difference
# Returns the difference between two Dates in the specified units; the result
# is floating-point and based on the average length of the unit.
#
# Args:
#   date
#   start
#   unit: One of 'year', 'month' 'week', 'day', 'hour', 'minute', or
#       'second'.
signatures.append({'args': [{'name': 'date', 'type': 'Date'}, {'name': 'start', 'type': 'Date'}, {'description': "One of 'year', 'month' 'week', 'day', 'hour', 'minute', or 'second'.", 'name': 'unit', 'type': 'String'}], 'description': 'Returns the difference between two Dates in the specified units; the result is floating-point and based on the average length of the unit.', 'returns': 'Float', 'type': 'Algorithm', 'hidden': False, 'name': 'Date.difference'})
# Date.format
# Convert a date to string.
#
# Args:
#   date
#   format: A pattern, as described at http://joda-time.sourceforge
#       .net/apidocs/org/joda/time/format/DateTimeFormat.html; if
#       omitted will use ISO standard date formatting.
#   timeZone: The time zone (e.g. 'America/Los_Angeles');
#       defaults to UTC.
signatures.append({'args': [{'name': 'date', 'type': 'Date'}, {'default': None, 'description': 'A pattern, as described at http://joda-time.sourceforge.net/apidocs/org/joda/time/format/DateTimeFormat.html; if omitted will use ISO standard date formatting.', 'name': 'format', 'optional': True, 'type': 'String'}, {'default': None, 'description': "The time zone (e.g. 'America/Los_Angeles'); defaults to UTC.", 'name': 'timeZone', 'optional': True, 'type': 'String'}], 'description': 'Convert a date to string.', 'returns': 'String', 'type': 'Algorithm', 'hidden': False, 'name': 'Date.format'})
# Date.fromYMD
# Returns a Date given year, month, day.
#
# Args:
#   year
#   month
#   day
#   timeZone: The time zone (e.g. 'America/Los_Angeles');
#       defaults to UTC.
signatures.append({'args': [{'name': 'year', 'type': 'Integer'}, {'name': 'month', 'type': 'Integer'}, {'name': 'day', 'type': 'Integer'}, {'default': None, 'description': "The time zone (e.g. 'America/Los_Angeles'); defaults to UTC.", 'name': 'timeZone', 'optional': True, 'type': 'String'}], 'description': 'Returns a Date given year, month, day.', 'returns': 'Date', 'type': 'Algorithm', 'hidden': False, 'name': 'Date.fromYMD'})
# Date.get
# Returns the specified unit of this date.
#
# Args:
#   date
#   unit: One of 'year', 'month' (returns 1-12), 'week' (1-53), 'day'
#       (1-31), 'hour' (0-23), 'minute' (0-59), or 'second' (0-59).
#   timeZone: The time zone (e.g. 'America/Los_Angeles');
#       defaults to UTC.
signatures.append({'args': [{'name': 'date', 'type': 'Date'}, {'description': "One of 'year', 'month' (returns 1-12), 'week' (1-53), 'day' (1-31), 'hour' (0-23), 'minute' (0-59), or 'second' (0-59).", 'name': 'unit', 'type': 'String'}, {'default': None, 'description': "The time zone (e.g. 'America/Los_Angeles'); defaults to UTC.", 'name': 'timeZone', 'optional': True, 'type': 'String'}], 'description': 'Returns the specified unit of this date.', 'returns': 'Long', 'type': 'Algorithm', 'hidden': False, 'name': 'Date.get'})
# Date.getFraction
# Returns this date's elapsed fraction of the specified unit (between 0 and
# 1).
#
# Args:
#   date
#   unit: One of 'year', 'month' 'week', 'day', 'hour', 'minute', or
#       'second'.
#   timeZone: The time zone (e.g. 'America/Los_Angeles');
#       defaults to UTC.
signatures.append({'args': [{'name': 'date', 'type': 'Date'}, {'description': "One of 'year', 'month' 'week', 'day', 'hour', 'minute', or 'second'.", 'name': 'unit', 'type': 'String'}, {'default': None, 'description': "The time zone (e.g. 'America/Los_Angeles'); defaults to UTC.", 'name': 'timeZone', 'optional': True, 'type': 'String'}], 'description': "Returns this date's elapsed fraction of the specified unit (between 0 and 1).", 'returns': 'Float', 'type': 'Algorithm', 'hidden': False, 'name': 'Date.getFraction'})
# Date.getRange
# Returns a DateRange covering the unit of the specified type that contains
# this date, e.g. Date('2013-3-15').getRange('year') returns
# DateRange('2013-1-1', '2014-1-1').
#
# Args:
#   date
#   unit: One of 'year', 'month' 'week', 'day', 'hour', 'minute', or
#       'second'.
#   timeZone: The time zone (e.g. 'America/Los_Angeles');
#       defaults to UTC.
signatures.append({'args': [{'name': 'date', 'type': 'Date'}, {'description': "One of 'year', 'month' 'week', 'day', 'hour', 'minute', or 'second'.", 'name': 'unit', 'type': 'String'}, {'default': None, 'description': "The time zone (e.g. 'America/Los_Angeles'); defaults to UTC.", 'name': 'timeZone', 'optional': True, 'type': 'String'}], 'description': "Returns a DateRange covering the unit of the specified type that contains this date, e.g. Date('2013-3-15').getRange('year') returns DateRange('2013-1-1', '2014-1-1').", 'returns': 'DateRange', 'type': 'Algorithm', 'hidden': False, 'name': 'Date.getRange'})
# Date.getRelative
# Returns the specified (0-based) unit of this date relative to a larger
# unit, e.g. getRelative('day', 'year') returns a value between 0 and 365.
#
# Args:
#   date
#   unit: One of 'month' 'week', 'day', 'hour', 'minute', or
#       'second'.
#   inUnit: One of 'year', 'month' 'week', 'day', 'hour', or
#       'minute'.
#   timeZone: The time zone (e.g. 'America/Los_Angeles');
#       defaults to UTC.
signatures.append({'args': [{'name': 'date', 'type': 'Date'}, {'description': "One of 'month' 'week', 'day', 'hour', 'minute', or 'second'.", 'name': 'unit', 'type': 'String'}, {'description': "One of 'year', 'month' 'week', 'day', 'hour', or 'minute'.", 'name': 'inUnit', 'type': 'String'}, {'default': None, 'description': "The time zone (e.g. 'America/Los_Angeles'); defaults to UTC.", 'name': 'timeZone', 'optional': True, 'type': 'String'}], 'description': "Returns the specified (0-based) unit of this date relative to a larger unit, e.g. getRelative('day', 'year') returns a value between 0 and 365.", 'returns': 'Long', 'type': 'Algorithm', 'hidden': False, 'name': 'Date.getRelative'})
# Date.millis
# The number of milliseconds since 1970-01-01T00:00:00Z.
#
# Args:
#   date
signatures.append({'args': [{'name': 'date', 'type': 'Date'}], 'description': 'The number of milliseconds since 1970-01-01T00:00:00Z.', 'returns': 'Long', 'type': 'Algorithm', 'hidden': False, 'name': 'Date.millis'})
# Date.parse
# Parse a date string, given a string describing its format.
#
# Args:
#   format: A pattern, as described at http://joda-time.sourceforge
#       .net/apidocs/org/joda/time/format/DateTimeFormat.html.
#   date: A string matching the given pattern.
#   timeZone: The time zone (e.g. 'America/Los_Angeles');
#       defaults to UTC.
signatures.append({'args': [{'description': 'A pattern, as described at http://joda-time.sourceforge.net/apidocs/org/joda/time/format/DateTimeFormat.html.', 'name': 'format', 'type': 'String'}, {'description': 'A string matching the given pattern.', 'name': 'date', 'type': 'String'}, {'default': None, 'description': "The time zone (e.g. 'America/Los_Angeles'); defaults to UTC.", 'name': 'timeZone', 'optional': True, 'type': 'String'}], 'description': 'Parse a date string, given a string describing its format.', 'returns': 'Date', 'type': 'Algorithm', 'hidden': False, 'name': 'Date.parse'})
# Date.unitRatio
# Returns the ratio of the length of one unit to the length of another, e.g.
# unitRatio('day', 'minute') returns 1440.  Valid units are 'year', 'month'
# 'week', 'day', 'hour', 'minute', and 'second'.
#
# Args:
#   numerator
#   denominator
signatures.append({'args': [{'name': 'numerator', 'type': 'String'}, {'name': 'denominator', 'type': 'String'}], 'description': "Returns the ratio of the length of one unit to the length of another, e.g. unitRatio('day', 'minute') returns 1440.  Valid units are 'year', 'month' 'week', 'day', 'hour', 'minute', and 'second'.", 'returns': 'Float', 'type': 'Algorithm', 'hidden': False, 'name': 'Date.unitRatio'})
# Date.update
# Create a new Date by setting one or more of the units of the given Date to
# a new value.  If a timeZone is given the new value(s) is interpreted in
# that zone.
#
# Args:
#   date
#   year
#   month
#   day
#   hour
#   minute
#   second
#   timeZone: The time zone (e.g. 'America/Los_Angeles');
#       defaults to UTC.
signatures.append({'args': [{'name': 'date', 'type': 'Date'}, {'default': None, 'name': 'year', 'optional': True, 'type': 'Integer'}, {'default': None, 'name': 'month', 'optional': True, 'type': 'Integer'}, {'default': None, 'name': 'day', 'optional': True, 'type': 'Integer'}, {'default': None, 'name': 'hour', 'optional': True, 'type': 'Integer'}, {'default': None, 'name': 'minute', 'optional': True, 'type': 'Integer'}, {'default': None, 'name': 'second', 'optional': True, 'type': 'Integer'}, {'default': None, 'description': "The time zone (e.g. 'America/Los_Angeles'); defaults to UTC.", 'name': 'timeZone', 'optional': True, 'type': 'String'}], 'description': 'Create a new Date by setting one or more of the units of the given Date to a new value.  If a timeZone is given the new value(s) is interpreted in that zone.', 'returns': 'Date', 'type': 'Algorithm', 'hidden': False, 'name': 'Date.update'})
# DateRange
# Creates a DateRange with the given start (inclusive) and end (exclusive),
# which may be Dates, numbers (interpreted as milliseconds since
# 1970-01-01T00:00:00Z), or strings (such as '1996-01-01T08:00'). If 'end' is
# not specified, a 1-millisecond range starting at 'start' is created.
#
# Args:
#   start
#   end
#   timeZone: If start and/or end are provided as strings, the
#       time zone in which to interpret them; defaults to UTC.
signatures.append({'args': [{'name': 'start', 'type': 'Object'}, {'default': None, 'name': 'end', 'optional': True, 'type': 'Object'}, {'default': None, 'description': 'If start and/or end are provided as strings, the time zone in which to interpret them; defaults to UTC.', 'name': 'timeZone', 'optional': True, 'type': 'String'}], 'description': "Creates a DateRange with the given start (inclusive) and end (exclusive), which may be Dates, numbers (interpreted as milliseconds since 1970-01-01T00:00:00Z), or strings (such as '1996-01-01T08:00'). If 'end' is not specified, a 1-millisecond range starting at 'start' is created.", 'returns': 'DateRange', 'type': 'Algorithm', 'hidden': False, 'name': 'DateRange'})
# DateRange.contains
# Returns true if the given Date or DateRange is within this DateRange.
#
# Args:
#   dateRange
#   other
signatures.append({'args': [{'name': 'dateRange', 'type': 'DateRange'}, {'name': 'other', 'type': 'Object'}], 'description': 'Returns true if the given Date or DateRange is within this DateRange.', 'returns': 'Boolean', 'type': 'Algorithm', 'hidden': False, 'name': 'DateRange.contains'})
# DateRange.end
# Returns the (exclusive) end of this DateRange.
#
# Args:
#   dateRange
signatures.append({'args': [{'name': 'dateRange', 'type': 'DateRange'}], 'description': 'Returns the (exclusive) end of this DateRange.', 'returns': 'Date', 'type': 'Algorithm', 'hidden': False, 'name': 'DateRange.end'})
# DateRange.intersection
# Returns a DateRange that contains all points in the intersection of this
# DateRange and another.
#
# Args:
#   dateRange
#   other
signatures.append({'args': [{'name': 'dateRange', 'type': 'DateRange'}, {'name': 'other', 'type': 'DateRange'}], 'description': 'Returns a DateRange that contains all points in the intersection of this DateRange and another.', 'returns': 'DateRange', 'type': 'Algorithm', 'hidden': False, 'name': 'DateRange.intersection'})
# DateRange.intersects
# Returns true if the given DateRange has at least one point in common with
# this DateRange.
#
# Args:
#   dateRange
#   other
signatures.append({'args': [{'name': 'dateRange', 'type': 'DateRange'}, {'name': 'other', 'type': 'DateRange'}], 'description': 'Returns true if the given DateRange has at least one point in common with this DateRange.', 'returns': 'Boolean', 'type': 'Algorithm', 'hidden': False, 'name': 'DateRange.intersects'})
# DateRange.isEmpty
# Returns true if this DateRange contains no dates (i.e. start >= end).
#
# Args:
#   dateRange
signatures.append({'args': [{'name': 'dateRange', 'type': 'DateRange'}], 'description': 'Returns true if this DateRange contains no dates (i.e. start >= end).', 'returns': 'Boolean', 'type': 'Algorithm', 'hidden': False, 'name': 'DateRange.isEmpty'})
# DateRange.isUnbounded
# Returns true if this DateRange contains all dates.
#
# Args:
#   dateRange
signatures.append({'args': [{'name': 'dateRange', 'type': 'DateRange'}], 'description': 'Returns true if this DateRange contains all dates.', 'returns': 'Boolean', 'type': 'Algorithm', 'hidden': False, 'name': 'DateRange.isUnbounded'})
# DateRange.start
# Returns the (inclusive) start of this DateRange.
#
# Args:
#   dateRange
signatures.append({'args': [{'name': 'dateRange', 'type': 'DateRange'}], 'description': 'Returns the (inclusive) start of this DateRange.', 'returns': 'Date', 'type': 'Algorithm', 'hidden': False, 'name': 'DateRange.start'})
# DateRange.unbounded
# Returns a DateRange that includes all possible dates.
signatures.append({'args': [], 'description': 'Returns a DateRange that includes all possible dates.', 'returns': 'DateRange', 'type': 'Algorithm', 'hidden': False, 'name': 'DateRange.unbounded'})
# DateRange.union
# Returns a DateRange that contains all points in the union of this DateRange
# and another.
#
# Args:
#   dateRange
#   other
signatures.append({'args': [{'name': 'dateRange', 'type': 'DateRange'}, {'name': 'other', 'type': 'DateRange'}], 'description': 'Returns a DateRange that contains all points in the union of this DateRange and another.', 'returns': 'DateRange', 'type': 'Algorithm', 'hidden': False, 'name': 'DateRange.union'})
# DateRangeCollection
# Returns a collection of objects with 'system:index', 'date_range'
# properties in a defined sequence at regular intervals, suitable for mapping
# over.
#
# Args:
#   startTime: The start time of the range, in msec since the
#       epoch.
#   endTime: The ending time of the range, in msec since the
#       epoch.
#   interval: The time interval between successive data ranges,
#       in units specified by 'units'.
#   units: The units in which 'period' is specified: currently only
#       'days' and 'years' are recognized.
#   resetAtYearBoundaries: If true, the intervals
#       will align to the start of each year.
signatures.append({'args': [{'description': 'The start time of the range, in msec since the epoch.', 'name': 'startTime', 'type': 'Long'}, {'description': 'The ending time of the range, in msec since the epoch.', 'name': 'endTime', 'type': 'Long'}, {'default': 1, 'description': "The time interval between successive data ranges, in units specified by 'units'.", 'name': 'interval', 'optional': True, 'type': 'Integer'}, {'default': 'days', 'description': "The units in which 'period' is specified: currently only 'days' and 'years' are recognized.", 'name': 'units', 'optional': True, 'type': 'String'}, {'default': False, 'description': 'If true, the intervals will align to the start of each year.', 'name': 'resetAtYearBoundaries', 'optional': True, 'type': 'Boolean'}], 'description': "Returns a collection of objects with 'system:index', 'date_range' properties in a defined sequence at regular intervals, suitable for mapping over.", 'returns': 'FeatureCollection', 'type': 'Algorithm', 'hidden': True, 'name': 'DateRangeCollection'})
# Describe
# Describes an object using a simple JSON-compatible structure.
#
# Args:
#   input: The object to describe.
signatures.append({'args': [{'description': 'The object to describe.', 'name': 'input', 'type': 'Object'}], 'description': 'Describes an object using a simple JSON-compatible structure.', 'returns': 'Object', 'type': 'Algorithm', 'hidden': False, 'name': 'Describe'})
# Dictionary
# Constructs a dictionary.
#
# Args:
#   input: An object to convert to a dictionary.  Either a JSON
#       dictionary or a list of alternating key/value pairs.  Keys
#       must be strings.
signatures.append({'args': [{'default': None, 'description': 'An object to convert to a dictionary.  Either a JSON dictionary or a list of alternating key/value pairs.  Keys must be strings.', 'name': 'input', 'optional': True, 'type': 'Object'}], 'description': 'Constructs a dictionary.', 'returns': 'Dictionary', 'type': 'Algorithm', 'hidden': False, 'name': 'Dictionary'})
# Dictionary.combine
# Combines two dictionaries.  In the case of duplicate names, the output will
# contain the value of the second dictionary unless overwrite is false.  Null
# values in both dictionaries are ignored / removed.
#
# Args:
#   first
#   second
#   overwrite
signatures.append({'args': [{'name': 'first', 'type': 'Dictionary'}, {'name': 'second', 'type': 'Dictionary'}, {'default': True, 'name': 'overwrite', 'optional': True, 'type': 'Boolean'}], 'description': 'Combines two dictionaries.  In the case of duplicate names, the output will contain the value of the second dictionary unless overwrite is false.  Null values in both dictionaries are ignored / removed.', 'returns': 'Dictionary', 'type': 'Algorithm', 'hidden': False, 'name': 'Dictionary.combine'})
# Dictionary.contains
# Returns true if the dictionary contains the given key.
#
# Args:
#   dictionary
#   key
signatures.append({'args': [{'name': 'dictionary', 'type': 'Dictionary'}, {'default': None, 'name': 'key', 'optional': True, 'type': 'String'}], 'description': 'Returns true if the dictionary contains the given key.', 'returns': 'Boolean', 'type': 'Algorithm', 'hidden': False, 'name': 'Dictionary.contains'})
# Dictionary.fromLists
# Construct a dictionary from two parallel lists of keys and values.
#
# Args:
#   keys
#   values
signatures.append({'args': [{'name': 'keys', 'type': 'List'}, {'name': 'values', 'type': 'List'}], 'description': 'Construct a dictionary from two parallel lists of keys and values.', 'returns': 'Dictionary', 'type': 'Algorithm', 'hidden': False, 'name': 'Dictionary.fromLists'})
# Dictionary.get
# Extracts a named value from a dictionary.
#
# Args:
#   dictionary
#   key
signatures.append({'args': [{'name': 'dictionary', 'type': 'Dictionary'}, {'name': 'key', 'type': 'String'}], 'description': 'Extracts a named value from a dictionary.', 'returns': 'Object', 'type': 'Algorithm', 'hidden': False, 'name': 'Dictionary.get'})
# Dictionary.keys
# Retrieve the keys of a dictionary as a list.  The keys will be sorted in
# natural order.
#
# Args:
#   dictionary
signatures.append({'args': [{'name': 'dictionary', 'type': 'Dictionary'}], 'description': 'Retrieve the keys of a dictionary as a list.  The keys will be sorted in natural order.', 'returns': 'List', 'type': 'Algorithm', 'hidden': False, 'name': 'Dictionary.keys'})
# Dictionary.map
# Map an algorithm over a dictionary.  The algorithm is expected to take 2
# arguments, a key from the existing dictionary and the value it corresponds
# to, and return a new value for the given key.  If the algorithm returns
# null, the key is dropped.
#
# Args:
#   dictionary
#   baseAlgorithm
signatures.append({'args': [{'name': 'dictionary', 'type': 'Dictionary'}, {'name': 'baseAlgorithm', 'type': 'Algorithm'}], 'description': 'Map an algorithm over a dictionary.  The algorithm is expected to take 2 arguments, a key from the existing dictionary and the value it corresponds to, and return a new value for the given key.  If the algorithm returns null, the key is dropped.', 'returns': 'Dictionary', 'type': 'Algorithm', 'hidden': False, 'name': 'Dictionary.map'})
# Dictionary.remove
# Returns a dictionary with the specified keys removed.
#
# Args:
#   dictionary
#   selectors: A list of keys names or regular expressions of
#       key names to remove.
#   ignoreMissing: Ignore selectors that don't match at
#       least 1 key.
signatures.append({'args': [{'name': 'dictionary', 'type': 'Dictionary'}, {'description': 'A list of keys names or regular expressions of key names to remove.', 'name': 'selectors', 'type': 'List'}, {'default': False, 'description': "Ignore selectors that don't match at least 1 key.", 'name': 'ignoreMissing', 'optional': True, 'type': 'Boolean'}], 'description': 'Returns a dictionary with the specified keys removed.', 'returns': 'Dictionary', 'type': 'Algorithm', 'hidden': False, 'name': 'Dictionary.remove'})
# Dictionary.rename
# Rename elements in a dictionary.
#
# Args:
#   dictionary
#   from: A list of keys to be renamed.
#   to: A list of the new names for the keys listed in the 'from'
#       parameter.  Must have the same length as the 'from' list.
#   overwrite: Allow overwriting existing properties with the
#       same name.
signatures.append({'args': [{'name': 'dictionary', 'type': 'Dictionary'}, {'description': 'A list of keys to be renamed.', 'name': 'from', 'type': 'List'}, {'description': "A list of the new names for the keys listed in the 'from' parameter.  Must have the same length as the 'from' list.", 'name': 'to', 'type': 'List'}, {'default': False, 'description': 'Allow overwriting existing properties with the same name.', 'name': 'overwrite', 'optional': True, 'type': 'Boolean'}], 'description': 'Rename elements in a dictionary.', 'returns': 'Dictionary', 'type': 'Algorithm', 'hidden': False, 'name': 'Dictionary.rename'})
# Dictionary.select
# Returns a dictionary with only the specified keys.
#
# Args:
#   dictionary
#   selectors: A list of keys or regular expressions to select.
#   ignoreMissing: Ignore selectors that don't match at
#       least 1 key.
signatures.append({'args': [{'name': 'dictionary', 'type': 'Dictionary'}, {'description': 'A list of keys or regular expressions to select.', 'name': 'selectors', 'type': 'List'}, {'default': False, 'description': "Ignore selectors that don't match at least 1 key.", 'name': 'ignoreMissing', 'optional': True, 'type': 'Boolean'}], 'description': 'Returns a dictionary with only the specified keys.', 'returns': 'Dictionary', 'type': 'Algorithm', 'hidden': False, 'name': 'Dictionary.select'})
# Dictionary.set
# Set a value in a dictionary.
#
# Args:
#   dictionary
#   key
#   value
signatures.append({'args': [{'name': 'dictionary', 'type': 'Dictionary'}, {'name': 'key', 'type': 'String'}, {'name': 'value', 'type': 'Object'}], 'description': 'Set a value in a dictionary.', 'returns': 'Object', 'type': 'Algorithm', 'hidden': False, 'name': 'Dictionary.set'})
# Dictionary.size
# Returns the number of entries in a dictionary.
#
# Args:
#   dictionary
signatures.append({'args': [{'name': 'dictionary', 'type': 'Dictionary'}], 'description': 'Returns the number of entries in a dictionary.', 'returns': 'Integer', 'type': 'Algorithm', 'hidden': False, 'name': 'Dictionary.size'})
# Dictionary.toArray
# Returns numeric values of a dictionary as an array. If no keys are
# specified, all values are returned in the natural ordering of the
# dictionary's keys. The default 'axis' is 0.
#
# Args:
#   dictionary
#   keys
#   axis
signatures.append({'args': [{'name': 'dictionary', 'type': 'Dictionary'}, {'default': None, 'name': 'keys', 'optional': True, 'type': 'List'}, {'default': 0, 'name': 'axis', 'optional': True, 'type': 'Integer'}], 'description': "Returns numeric values of a dictionary as an array. If no keys are specified, all values are returned in the natural ordering of the dictionary's keys. The default 'axis' is 0.", 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Dictionary.toArray'})
# Dictionary.toImage
# Creates an image of constants from values in a dictionary. The bands of the
# image are ordered and named according to the names argument.  If no names
# are specified, the bands are sorted alpha-numerically.
#
# Args:
#   dictionary: The dictionary to convert.
#   names: The order of the output bands.
signatures.append({'args': [{'description': 'The dictionary to convert.', 'name': 'dictionary', 'type': 'Dictionary'}, {'default': None, 'description': 'The order of the output bands.', 'name': 'names', 'optional': True, 'type': 'List'}], 'description': 'Creates an image of constants from values in a dictionary. The bands of the image are ordered and named according to the names argument.  If no names are specified, the bands are sorted alpha-numerically.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Dictionary.toImage'})
# Dictionary.values
# Returns the values of a dictionary as a list.  If no keys are specified,
# all values are returned in the natural ordering of the dictionary's keys.
#
# Args:
#   dictionary
#   keys
signatures.append({'args': [{'name': 'dictionary', 'type': 'Dictionary'}, {'default': None, 'name': 'keys', 'optional': True, 'type': 'List'}], 'description': "Returns the values of a dictionary as a list.  If no keys are specified, all values are returned in the natural ordering of the dictionary's keys.", 'returns': 'List', 'type': 'Algorithm', 'hidden': False, 'name': 'Dictionary.values'})
# Element.copyProperties
# Copies metadata properties from one element to another.
#
# Args:
#   destination: The object whose properties to override.
#   source: The object from which to copy the properties.
#   properties: The properties to copy.  If omitted, all
#       ordinary (i.e. non-system) properties are copied.
#   exclude: The list of properties to exclude when copying all
#       properties. Must not be specified if properties is.
signatures.append({'args': [{'default': None, 'description': 'The object whose properties to override.', 'name': 'destination', 'optional': True, 'type': 'Element'}, {'default': None, 'description': 'The object from which to copy the properties.', 'name': 'source', 'optional': True, 'type': 'Element'}, {'default': None, 'description': 'The properties to copy.  If omitted, all ordinary (i.e. non-system) properties are copied.', 'name': 'properties', 'optional': True, 'type': 'List'}, {'default': None, 'description': 'The list of properties to exclude when copying all properties. Must not be specified if properties is.', 'name': 'exclude', 'optional': True, 'type': 'List'}], 'description': 'Copies metadata properties from one element to another.', 'returns': 'Element', 'type': 'Algorithm', 'hidden': False, 'name': 'Element.copyProperties'})
# Element.geometry
# Returns the geometry of a given feature in a given projection.
#
# Args:
#   feature: The feature from which the geometry is taken.
#   maxError: The maximum amount of error tolerated when
#       performing any necessary reprojection.
#   proj: If specified, the geometry will be in this projection. If
#       unspecified, the geometry will be in its default projection.
#   geodesics: If true, the geometry will have geodesic edges.
#       If false, it will have edges as straight lines in the
#       specified projection. If null, the edge interpretation
#       will be the same as the original geometry. This argument
#       is ignored if proj is not specified.
signatures.append({'args': [{'description': 'The feature from which the geometry is taken.', 'name': 'feature', 'type': 'Element'}, {'default': None, 'description': 'The maximum amount of error tolerated when performing any necessary reprojection.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}, {'default': None, 'description': 'If specified, the geometry will be in this projection. If unspecified, the geometry will be in its default projection.', 'name': 'proj', 'optional': True, 'type': 'Projection'}, {'default': None, 'description': 'If true, the geometry will have geodesic edges. If false, it will have edges as straight lines in the specified projection. If null, the edge interpretation will be the same as the original geometry. This argument is ignored if proj is not specified.', 'name': 'geodesics', 'optional': True, 'type': 'Boolean'}], 'description': 'Returns the geometry of a given feature in a given projection.', 'returns': 'Geometry', 'type': 'Algorithm', 'hidden': False, 'name': 'Element.geometry'})
# Element.get
# Extract a property from a feature.
#
# Args:
#   object: The feature to extract the property from.
#   property: The property to extract.
signatures.append({'args': [{'description': 'The feature to extract the property from.', 'name': 'object', 'type': 'Element'}, {'description': 'The property to extract.', 'name': 'property', 'type': 'String'}], 'description': 'Extract a property from a feature.', 'returns': '', 'type': 'Algorithm', 'hidden': False, 'name': 'Element.get'})
# Element.propertyNames
# Returns the names of properties on this element.
#
# Args:
#   element
signatures.append({'args': [{'name': 'element', 'type': 'Element'}], 'description': 'Returns the names of properties on this element.', 'returns': 'List', 'type': 'Algorithm', 'hidden': False, 'name': 'Element.propertyNames'})
# Element.set
# Overrides a metadata property of an object.
#
# Args:
#   object: The object on which to set the property.
#   key: The name of the property to set.
#   value: The new value of the property.
signatures.append({'args': [{'description': 'The object on which to set the property.', 'name': 'object', 'type': 'Element'}, {'description': 'The name of the property to set.', 'name': 'key', 'type': 'String'}, {'default': None, 'description': 'The new value of the property.', 'name': 'value', 'optional': True, 'type': 'Object'}], 'description': 'Overrides a metadata property of an object.', 'returns': 'Element', 'type': 'Algorithm', 'hidden': False, 'name': 'Element.set'})
# Element.setMulti
# Overrides one or more metadata properties of an object.
#
# Args:
#   object: The object whose properties to override.
#   properties: The property values to override.
signatures.append({'args': [{'description': 'The object whose properties to override.', 'name': 'object', 'type': 'Element'}, {'description': 'The property values to override.', 'name': 'properties', 'type': 'Dictionary'}], 'description': 'Overrides one or more metadata properties of an object.', 'returns': 'Element', 'type': 'Algorithm', 'hidden': False, 'name': 'Element.setMulti'})
# Element.toDictionary
# Extract properties from a feature as a dictionary.
#
# Args:
#   element: The feature to extract the property from.
#   properties: The list of properties to extract.  Defaults to
#       all non-system properties.
signatures.append({'args': [{'description': 'The feature to extract the property from.', 'name': 'element', 'type': 'Element'}, {'default': None, 'description': 'The list of properties to extract.  Defaults to all non-system properties.', 'name': 'properties', 'optional': True, 'type': 'List'}], 'description': 'Extract properties from a feature as a dictionary.', 'returns': 'Dictionary', 'type': 'Algorithm', 'hidden': False, 'name': 'Element.toDictionary'})
# ErrorMargin
# Returns an ErrorMargin of the given type with the given value.
#
# Args:
#   value: The maximum error value allowed by the margin. Ignored if
#       the unit is 'infinite'.
#   unit: The unit of this margin: 'meters', 'projected' or
#       'infinite'.
signatures.append({'args': [{'default': None, 'description': "The maximum error value allowed by the margin. Ignored if the unit is 'infinite'.", 'name': 'value', 'optional': True, 'type': 'Float'}, {'default': 'meters', 'description': "The unit of this margin: 'meters', 'projected' or 'infinite'.", 'name': 'unit', 'optional': True, 'type': 'String'}], 'description': 'Returns an ErrorMargin of the given type with the given value.', 'returns': 'ErrorMargin', 'type': 'Algorithm', 'hidden': False, 'name': 'ErrorMargin'})
# ExtractRegion.AggregationContainer
# INTERNAL
#
# Args:
#   input
#   proj
#   geom
signatures.append({'args': [{'name': 'input', 'type': 'ImageCollection'}, {'name': 'proj', 'type': 'Projection'}, {'name': 'geom', 'type': 'Geometry'}], 'description': 'INTERNAL', 'returns': 'Image', 'type': 'Algorithm', 'hidden': True, 'name': 'ExtractRegion.AggregationContainer'})
# FMask.fillMinima
# Fills local minima.  Only works on INT types.
#
# Args:
#   image: The image to fill.
#   borderValue: The border value.
#   neighborhood: The size of the neighborhood to compute
#       over.
signatures.append({'args': [{'description': 'The image to fill.', 'name': 'image', 'type': 'Image'}, {'default': None, 'description': 'The border value.', 'name': 'borderValue', 'optional': True, 'type': 'Long'}, {'default': 50, 'description': 'The size of the neighborhood to compute over.', 'name': 'neighborhood', 'optional': True, 'type': 'Integer'}], 'description': 'Fills local minima.  Only works on INT types.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'FMask.fillMinima'})
# FMask.matchClouds
# Runs the FMask cloud and shadow matching.  Outputs a single band ('csm'),
# containing the computed cloud and shadow masks.
#
# Args:
#   input: The scene for which to compute cloud and shadow masks.
#   cloud: Potential cloud mask image. Expected to contain 1s for
#       cloudy pixels and masked pixels everywhere else.
#   shadow: Potential shadow mask image. Expected to contain 1s for
#       shadow pixels and masked pixels everywhere else.
#   btemp: Brightness temperature image, in Celsius.
#   sceneLow: The 0.175 percentile brightness temperature of the
#       scene.
#   sceneHigh: The 0.825 percentile brightness temperature of
#       the scene.
#   neighborhood: The neighborhood to pad around each tile.
signatures.append({'args': [{'description': 'The scene for which to compute cloud and shadow masks.', 'name': 'input', 'type': 'Image'}, {'description': 'Potential cloud mask image. Expected to contain 1s for cloudy pixels and masked pixels everywhere else.', 'name': 'cloud', 'type': 'Image'}, {'description': 'Potential shadow mask image. Expected to contain 1s for shadow pixels and masked pixels everywhere else.', 'name': 'shadow', 'type': 'Image'}, {'description': 'Brightness temperature image, in Celsius.', 'name': 'btemp', 'type': 'Image'}, {'description': 'The 0.175 percentile brightness temperature of the scene.', 'name': 'sceneLow', 'type': 'Float'}, {'description': 'The 0.825 percentile brightness temperature of the scene.', 'name': 'sceneHigh', 'type': 'Float'}, {'default': 50, 'description': 'The neighborhood to pad around each tile.', 'name': 'neighborhood', 'optional': True, 'type': 'Integer'}], 'description': "Runs the FMask cloud and shadow matching.  Outputs a single band ('csm'), containing the computed cloud and shadow masks.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'FMask.matchClouds'})
# Feature
# Returns a Feature composed of the given geometry and metadata.
#
# Args:
#   geometry: The geometry of the feature.
#   metadata: The properties of the feature.
#   geometryKey: Obsolete; has no effect.
signatures.append({'args': [{'default': None, 'description': 'The geometry of the feature.', 'name': 'geometry', 'optional': True, 'type': 'Geometry'}, {'default': {}, 'description': 'The properties of the feature.', 'name': 'metadata', 'optional': True, 'type': 'Dictionary'}, {'default': None, 'description': 'Obsolete; has no effect.', 'name': 'geometryKey', 'optional': True, 'type': 'String'}], 'description': 'Returns a Feature composed of the given geometry and metadata.', 'returns': 'Feature', 'type': 'Algorithm', 'hidden': False, 'name': 'Feature'})
# Feature.area
# Returns the area of the feature's default geometry. Area of points and line
# strings is 0, and the area of multi geometries is the sum of the areas of
# their componenets (intersecting areas are counted multiple times).
#
# Args:
#   feature: The feature from which the geometry is taken.
#   maxError: The maximum amount of error tolerated when
#       performing any  necessary reprojection.
#   proj: If specified, the result will be in the units of the
#       coordinate system of this projection. Otherwise it  will be
#       in square meters.
signatures.append({'args': [{'description': 'The feature from which the geometry is taken.', 'name': 'feature', 'type': 'Element'}, {'default': None, 'description': 'The maximum amount of error tolerated when performing any  necessary reprojection.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}, {'default': None, 'description': 'If specified, the result will be in the units of the coordinate system of this projection. Otherwise it  will be in square meters.', 'name': 'proj', 'optional': True, 'type': 'Projection'}], 'description': "Returns the area of the feature's default geometry. Area of points and line strings is 0, and the area of multi geometries is the sum of the areas of their componenets (intersecting areas are counted multiple times).", 'returns': 'Float', 'type': 'Algorithm', 'hidden': False, 'name': 'Feature.area'})
# Feature.bounds
# Returns a feature containing the bounding box of the geometry of a given
# feature.
#
# Args:
#   feature: The feature the bound of which is being calculated.
#   maxError: The maximum amount of error tolerated when
#       performing any necessary reprojection.
#   proj: If specified, the result will be in this projection.
#       Otherwise it will be in WGS84.
signatures.append({'args': [{'description': 'The feature the bound of which is being calculated.', 'name': 'feature', 'type': 'Element'}, {'default': None, 'description': 'The maximum amount of error tolerated when performing any necessary reprojection.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}, {'default': None, 'description': 'If specified, the result will be in this projection. Otherwise it will be in WGS84.', 'name': 'proj', 'optional': True, 'type': 'Projection'}], 'description': 'Returns a feature containing the bounding box of the geometry of a given feature.', 'returns': 'Feature', 'type': 'Algorithm', 'hidden': False, 'name': 'Feature.bounds'})
# Feature.buffer
# Returns the input buffered by a given distance. If the distance is
# positive, the geometry is expanded, and if the distance is negative, the
# geometry is contracted.
#
# Args:
#   feature: The feature the geometry of which is being buffered.
#   distance: The distance of the buffering, which may be
#       negative. If no projection is specified, the unit is
#       meters. Otherwise the unit is in the coordinate system of
#       the projection.
#   maxError: The maximum amount of error tolerated when
#       approximating the buffering circle and performing any
#       necessary reprojection. If unspecified, defaults to 1% of
#       the distance.
#   proj: If specified, the buffering will be performed in this
#       projection and the distance will be interpreted as units of
#       the coordinate system of this projection. Otherwise the
#       distance is interpereted as meters and the buffering is
#       performed in a spherical coordinate system.
signatures.append({'args': [{'description': 'The feature the geometry of which is being buffered.', 'name': 'feature', 'type': 'Element'}, {'description': 'The distance of the buffering, which may be negative. If no projection is specified, the unit is meters. Otherwise the unit is in the coordinate system of the projection.', 'name': 'distance', 'type': 'Float'}, {'default': None, 'description': 'The maximum amount of error tolerated when approximating the buffering circle and performing any necessary reprojection. If unspecified, defaults to 1% of the distance.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}, {'default': None, 'description': 'If specified, the buffering will be performed in this projection and the distance will be interpreted as units of the coordinate system of this projection. Otherwise the distance is interpereted as meters and the buffering is performed in a spherical coordinate system.', 'name': 'proj', 'optional': True, 'type': 'Projection'}], 'description': 'Returns the input buffered by a given distance. If the distance is positive, the geometry is expanded, and if the distance is negative, the geometry is contracted.', 'returns': 'Feature', 'type': 'Algorithm', 'hidden': False, 'name': 'Feature.buffer'})
# Feature.centroid
# Returns a feature containing the point at the center of the highest-
# dimension components of the geometry of a feature. Lower-dimensional
# components are ignored, so the centroid of a geometry containing two
# polygons, three lines and a point is equivalent to the centroid of a
# geometry containing just the two polygons.
#
# Args:
#   feature: Calculates the centroid of this feature's default
#       geometry.
#   maxError: The maximum amount of error tolerated when
#       performing any necessary reprojection.
#   proj: If specified, the result will be in this projection.
#       Otherwise it will be in WGS84.
signatures.append({'args': [{'description': "Calculates the centroid of this feature's default geometry.", 'name': 'feature', 'type': 'Element'}, {'default': None, 'description': 'The maximum amount of error tolerated when performing any necessary reprojection.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}, {'default': None, 'description': 'If specified, the result will be in this projection. Otherwise it will be in WGS84.', 'name': 'proj', 'optional': True, 'type': 'Projection'}], 'description': 'Returns a feature containing the point at the center of the highest-dimension components of the geometry of a feature. Lower-dimensional components are ignored, so the centroid of a geometry containing two polygons, three lines and a point is equivalent to the centroid of a geometry containing just the two polygons.', 'returns': 'Feature', 'type': 'Algorithm', 'hidden': False, 'name': 'Feature.centroid'})
# Feature.containedIn
# Returns true iff the geometry of one feature is contained in the geometry
# of another.
#
# Args:
#   left: The feature containing the geometry used as the left
#       operand of the operation.
#   right: The feature containing the geometry used as the right
#       operand of the operation.
#   maxError: The maximum amount of error tolerated when
#       performing any necessary reprojection.
#   proj: The projection in which to perform the operation. If not
#       specified, the operation will be performed in a spherical
#       coordinate system, and linear distances will be in meters on
#       the sphere.
signatures.append({'args': [{'description': 'The feature containing the geometry used as the left operand of the operation.', 'name': 'left', 'type': 'Element'}, {'description': 'The feature containing the geometry used as the right operand of the operation.', 'name': 'right', 'type': 'Element'}, {'default': None, 'description': 'The maximum amount of error tolerated when performing any necessary reprojection.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}, {'default': None, 'description': 'The projection in which to perform the operation. If not specified, the operation will be performed in a spherical coordinate system, and linear distances will be in meters on the sphere.', 'name': 'proj', 'optional': True, 'type': 'Projection'}], 'description': 'Returns true iff the geometry of one feature is contained in the geometry of another.', 'returns': 'Boolean', 'type': 'Algorithm', 'hidden': False, 'name': 'Feature.containedIn'})
# Feature.contains
# Returns true iff the geometry of one feature contains the geometry of
# another.
#
# Args:
#   left: The feature containing the geometry used as the left
#       operand of the operation.
#   right: The feature containing the geometry used as the right
#       operand of the operation.
#   maxError: The maximum amount of error tolerated when
#       performing any necessary reprojection.
#   proj: The projection in which to perform the operation. If not
#       specified, the operation will be performed in a spherical
#       coordinate system, and linear distances will be in meters on
#       the sphere.
signatures.append({'args': [{'description': 'The feature containing the geometry used as the left operand of the operation.', 'name': 'left', 'type': 'Element'}, {'description': 'The feature containing the geometry used as the right operand of the operation.', 'name': 'right', 'type': 'Element'}, {'default': None, 'description': 'The maximum amount of error tolerated when performing any necessary reprojection.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}, {'default': None, 'description': 'The projection in which to perform the operation. If not specified, the operation will be performed in a spherical coordinate system, and linear distances will be in meters on the sphere.', 'name': 'proj', 'optional': True, 'type': 'Projection'}], 'description': 'Returns true iff the geometry of one feature contains the geometry of another.', 'returns': 'Boolean', 'type': 'Algorithm', 'hidden': False, 'name': 'Feature.contains'})
# Feature.convexHull
# Returns the feature, with the geometry replaced by the convex hull of the
# original geometry. The convex hull of a single point is the point itself,
# the convex hull of collinear points is a line, and the convex hull of
# everything else is a polygon. Note that a degenerate polygon with all
# vertices on the same line will result in a line segment.
#
# Args:
#   feature: The feature containing the geometry whole hull is
#       being calculated.
#   maxError: The maximum amount of error tolerated when
#       performing any necessary reprojection.
#   proj: The projection in which to perform the operation. If not
#       specified, the operation will be performed in a spherical
#       coordinate system, and linear distances will be in meters on
#       the sphere.
signatures.append({'args': [{'description': 'The feature containing the geometry whole hull is being calculated.', 'name': 'feature', 'type': 'Element'}, {'default': None, 'description': 'The maximum amount of error tolerated when performing any necessary reprojection.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}, {'default': None, 'description': 'The projection in which to perform the operation. If not specified, the operation will be performed in a spherical coordinate system, and linear distances will be in meters on the sphere.', 'name': 'proj', 'optional': True, 'type': 'Projection'}], 'description': 'Returns the feature, with the geometry replaced by the convex hull of the original geometry. The convex hull of a single point is the point itself, the convex hull of collinear points is a line, and the convex hull of  everything else is a polygon. Note that a degenerate polygon with all vertices on the same line will result in a line segment.', 'returns': 'Feature', 'type': 'Algorithm', 'hidden': False, 'name': 'Feature.convexHull'})
# Feature.cutLines
# Converts LineStrings into a MultiLineString by cutting it in two at each
# distance along the length of the LineString.
#
# Args:
#   feature: Cuts the lines of this feature's default geometry.
#   distances: Distances along each LineString to cut the line
#       into separate pieces, measured in units of the given
#       proj, or meters if proj is unspecified.
#   maxError: The maximum amount of error tolerated when
#       performing any necessary reprojection.
#   proj: Projection of the result and distance measurements, or
#       WGS84 if unspecified.
signatures.append({'args': [{'description': "Cuts the lines of this feature's default geometry.", 'name': 'feature', 'type': 'Element'}, {'description': 'Distances along each LineString to cut the line into separate pieces, measured in units of the given proj, or meters if proj is unspecified.', 'name': 'distances', 'type': 'List'}, {'default': None, 'description': 'The maximum amount of error tolerated when performing any necessary reprojection.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}, {'default': None, 'description': 'Projection of the result and distance measurements, or WGS84 if unspecified.', 'name': 'proj', 'optional': True, 'type': 'Projection'}], 'description': 'Converts LineStrings into a MultiLineString by cutting it in two at each distance along the length of the LineString.', 'returns': 'Feature', 'type': 'Algorithm', 'hidden': False, 'name': 'Feature.cutLines'})
# Feature.difference
# Returns a feature with the properties of the 'left' feature, and the
# geometry that results from subtracting the 'right' geometry from the 'left'
# geometry.
#
# Args:
#   left: The feature containing the geometry used as the left
#       operand of the operation. The properties of the result will
#       be copied from this object.
#   right: The feature containing the geometry used as the right
#       operand of the operation. The properties of this object are
#       ignored.
#   maxError: The maximum amount of error tolerated when
#       performing any necessary reprojection.
#   proj: The projection in which to perform the operation. If not
#       specified, the operation will be performed in a spherical
#       coordinate system, and linear distances will be in meters on
#       the sphere.
signatures.append({'args': [{'description': 'The feature containing the geometry used as the left operand of the operation. The properties of the result will be copied from this object.', 'name': 'left', 'type': 'Element'}, {'description': 'The feature containing the geometry used as the right operand of the operation. The properties of this object are ignored.', 'name': 'right', 'type': 'Element'}, {'default': None, 'description': 'The maximum amount of error tolerated when performing any necessary reprojection.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}, {'default': None, 'description': 'The projection in which to perform the operation. If not specified, the operation will be performed in a spherical coordinate system, and linear distances will be in meters on the sphere.', 'name': 'proj', 'optional': True, 'type': 'Projection'}], 'description': "Returns a feature with the properties of the 'left' feature, and the geometry that results from subtracting the 'right' geometry from the 'left' geometry.", 'returns': 'Feature', 'type': 'Algorithm', 'hidden': False, 'name': 'Feature.difference'})
# Feature.disjoint
# Returns true iff the feature geometries are disjoint.
#
# Args:
#   left: The feature containing the geometry used as the left
#       operand of the operation.
#   right: The feature containing the geometry used as the right
#       operand of the operation.
#   maxError: The maximum amount of error tolerated when
#       performing any necessary reprojection.
#   proj: The projection in which to perform the operation. If not
#       specified, the operation will be performed in a spherical
#       coordinate system, and linear distances will be in meters on
#       the sphere.
signatures.append({'args': [{'description': 'The feature containing the geometry used as the left operand of the operation.', 'name': 'left', 'type': 'Element'}, {'description': 'The feature containing the geometry used as the right operand of the operation.', 'name': 'right', 'type': 'Element'}, {'default': None, 'description': 'The maximum amount of error tolerated when performing any necessary reprojection.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}, {'default': None, 'description': 'The projection in which to perform the operation. If not specified, the operation will be performed in a spherical coordinate system, and linear distances will be in meters on the sphere.', 'name': 'proj', 'optional': True, 'type': 'Projection'}], 'description': 'Returns true iff the feature geometries are disjoint.', 'returns': 'Boolean', 'type': 'Algorithm', 'hidden': False, 'name': 'Feature.disjoint'})
# Feature.dissolve
# Returns a feature containing the union of the geometry of a feature. This
# leaves single geometries untouched, and unions multi geometries.
#
# Args:
#   feature: The feature the geometry of which is being unioned.
#   maxError: The maximum amount of error tolerated when
#       performing any  necessary reprojection.
#   proj: If specified, the union will be performed in this
#       projection. Otherwise it will be performed in a spherical
#       coordinate system.
signatures.append({'args': [{'description': 'The feature the geometry of which is being unioned.', 'name': 'feature', 'type': 'Element'}, {'default': None, 'description': 'The maximum amount of error tolerated when performing any  necessary reprojection.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}, {'default': None, 'description': 'If specified, the union will be performed in this projection. Otherwise it will be performed in a spherical coordinate system.', 'name': 'proj', 'optional': True, 'type': 'Projection'}], 'description': 'Returns a feature containing the union of the geometry of a feature. This leaves single geometries untouched, and unions multi geometries.', 'returns': 'Element', 'type': 'Algorithm', 'hidden': False, 'name': 'Feature.dissolve'})
# Feature.distance
# Returns the minimum distance between the geometries of two features.
#
# Args:
#   left: The feature containing the geometry used as the left
#       operand of the operation.
#   right: The feature containing the geometry used as the right
#       operand of the operation.
#   maxError: The maximum amount of error tolerated when
#       performing any necessary reprojection.
#   proj: The projection in which to perform the operation. If not
#       specified, the operation will be performed in a spherical
#       coordinate system, and linear distances will be in meters on
#       the sphere.
signatures.append({'args': [{'description': 'The feature containing the geometry used as the left operand of the operation.', 'name': 'left', 'type': 'Element'}, {'description': 'The feature containing the geometry used as the right operand of the operation.', 'name': 'right', 'type': 'Element'}, {'default': None, 'description': 'The maximum amount of error tolerated when performing any necessary reprojection.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}, {'default': None, 'description': 'The projection in which to perform the operation. If not specified, the operation will be performed in a spherical coordinate system, and linear distances will be in meters on the sphere.', 'name': 'proj', 'optional': True, 'type': 'Projection'}], 'description': 'Returns the minimum distance between the geometries of two features.', 'returns': 'Float', 'type': 'Algorithm', 'hidden': False, 'name': 'Feature.distance'})
# Feature.geometry
# Returns the geometry of a given feature in a given projection.
#
# Args:
#   feature: The feature from which the geometry is taken.
#   maxError: The maximum amount of error tolerated when
#       performing any necessary reprojection.
#   proj: If specified, the geometry will be in this projection. If
#       unspecified, the geometry will be in its default projection.
#   geodesics: If true, the geometry will have geodesic edges.
#       If false, it will have edges as straight lines in the
#       specified projection. If null, the edge interpretation
#       will be the same as the original geometry. This argument
#       is ignored if proj is not specified.
signatures.append({'args': [{'description': 'The feature from which the geometry is taken.', 'name': 'feature', 'type': 'Element'}, {'default': None, 'description': 'The maximum amount of error tolerated when performing any necessary reprojection.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}, {'default': None, 'description': 'If specified, the geometry will be in this projection. If unspecified, the geometry will be in its default projection.', 'name': 'proj', 'optional': True, 'type': 'Projection'}, {'default': None, 'description': 'If true, the geometry will have geodesic edges. If false, it will have edges as straight lines in the specified projection. If null, the edge interpretation will be the same as the original geometry. This argument is ignored if proj is not specified.', 'name': 'geodesics', 'optional': True, 'type': 'Boolean'}], 'description': 'Returns the geometry of a given feature in a given projection.', 'returns': 'Geometry', 'type': 'Algorithm', 'hidden': False, 'deprecated': 'Use Element.geometry()', 'name': 'Feature.geometry'})
# Feature.id
# Returns the ID of a given element within a collection. Objects outside
# collections are not guaranteed to have IDs.
#
# Args:
#   element: The element from which the ID is taken.
signatures.append({'args': [{'description': 'The element from which the ID is taken.', 'name': 'element', 'type': 'Element'}], 'description': 'Returns the ID of a given element within a collection. Objects outside collections are not guaranteed to have IDs.', 'returns': 'String', 'type': 'Algorithm', 'hidden': False, 'name': 'Feature.id'})
# Feature.intersection
# Returns a feature containing the intersection of the geometries of two
# features, with the properties of the left feature.
#
# Args:
#   left: The feature containing the geometry used as the left
#       operand of the operation. The properties of the result will
#       be copied from this object.
#   right: The feature containing the geometry used as the right
#       operand of the operation. The properties of this object are
#       ignored.
#   maxError: The maximum amount of error tolerated when
#       performing any necessary reprojection.
#   proj: The projection in which to perform the operation. If not
#       specified, the operation will be performed in a spherical
#       coordinate system, and linear distances will be in meters on
#       the sphere.
signatures.append({'args': [{'description': 'The feature containing the geometry used as the left operand of the operation. The properties of the result will be copied from this object.', 'name': 'left', 'type': 'Element'}, {'description': 'The feature containing the geometry used as the right operand of the operation. The properties of this object are ignored.', 'name': 'right', 'type': 'Element'}, {'default': None, 'description': 'The maximum amount of error tolerated when performing any necessary reprojection.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}, {'default': None, 'description': 'The projection in which to perform the operation. If not specified, the operation will be performed in a spherical coordinate system, and linear distances will be in meters on the sphere.', 'name': 'proj', 'optional': True, 'type': 'Projection'}], 'description': 'Returns a feature containing the intersection of the geometries of two features, with the properties of the left feature.', 'returns': 'Feature', 'type': 'Algorithm', 'hidden': False, 'name': 'Feature.intersection'})
# Feature.intersects
# Returns true iff the feature geometries intersect.
#
# Args:
#   left: The feature containing the geometry used as the left
#       operand of the operation.
#   right: The feature containing the geometry used as the right
#       operand of the operation.
#   maxError: The maximum amount of error tolerated when
#       performing any necessary reprojection.
#   proj: The projection in which to perform the operation. If not
#       specified, the operation will be performed in a spherical
#       coordinate system, and linear distances will be in meters on
#       the sphere.
signatures.append({'args': [{'description': 'The feature containing the geometry used as the left operand of the operation.', 'name': 'left', 'type': 'Element'}, {'description': 'The feature containing the geometry used as the right operand of the operation.', 'name': 'right', 'type': 'Element'}, {'default': None, 'description': 'The maximum amount of error tolerated when performing any necessary reprojection.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}, {'default': None, 'description': 'The projection in which to perform the operation. If not specified, the operation will be performed in a spherical coordinate system, and linear distances will be in meters on the sphere.', 'name': 'proj', 'optional': True, 'type': 'Projection'}], 'description': 'Returns true iff the feature geometries intersect.', 'returns': 'Boolean', 'type': 'Algorithm', 'hidden': False, 'name': 'Feature.intersects'})
# Feature.length
# Returns the length of the linear parts of the geometry of a given feature.
# Polygonal parts are ignored. The length of multi geometries is the sum of
# the lengths of their components.
#
# Args:
#   feature: The feature from which the geometry is taken.
#   maxError: The maximum amount of error tolerated when
#       performing any necessary reprojection.
#   proj: If specified, the result will be in the units of the
#       coordinate system of this projection. Otherwise it will be in
#       meters.
signatures.append({'args': [{'description': 'The feature from which the geometry is taken.', 'name': 'feature', 'type': 'Element'}, {'default': None, 'description': 'The maximum amount of error tolerated when performing any necessary reprojection.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}, {'default': None, 'description': 'If specified, the result will be in the units of the coordinate system of this projection. Otherwise it will be in meters.', 'name': 'proj', 'optional': True, 'type': 'Projection'}], 'description': 'Returns the length of the linear parts of the geometry of a given feature. Polygonal parts are ignored. The length of multi geometries is the sum of the lengths of their components.', 'returns': 'Float', 'type': 'Algorithm', 'hidden': False, 'name': 'Feature.length'})
# Feature.perimeter
# Returns the length of the perimeter of the polygonal parts of the geometry
# of a given feature. The perimeter of multi geometries is the sum of the
# perimeters of their components.
#
# Args:
#   feature: The feature from which the geometry is taken.
#   maxError: The maximum amount of error tolerated when
#       performing any necessary reprojection.
#   proj: If specified, the result will be in the units of the
#       coordinate system of this projection. Otherwise it will be in
#       meters.
signatures.append({'args': [{'description': 'The feature from which the geometry is taken.', 'name': 'feature', 'type': 'Element'}, {'default': None, 'description': 'The maximum amount of error tolerated when performing any necessary reprojection.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}, {'default': None, 'description': 'If specified, the result will be in the units of the coordinate system of this projection. Otherwise it will be in meters.', 'name': 'proj', 'optional': True, 'type': 'Projection'}], 'description': 'Returns the length of the perimeter of the polygonal parts of the geometry of a given feature. The perimeter of multi geometries is the sum of the perimeters of their components.', 'returns': 'Float', 'type': 'Algorithm', 'hidden': False, 'name': 'Feature.perimeter'})
# Feature.select
# Selects properties from a feature by name or RE2-compatible regex and
# optionally renames them.
#
# Args:
#   input: The feature to select properties from.
#   propertySelectors: A list of names or regexes
#       specifying the properties to select.
#   newProperties: Optional new names for the output
#       properties.  Must match the number of properties
#       selected.
#   retainGeometry: When false, the result will have a NULL
#       geometry.
signatures.append({'args': [{'description': 'The feature to select properties from.', 'name': 'input', 'type': 'Element'}, {'description': 'A list of names or regexes specifying the properties to select.', 'name': 'propertySelectors', 'type': 'List'}, {'default': None, 'description': 'Optional new names for the output properties.  Must match the number of properties selected.', 'name': 'newProperties', 'optional': True, 'type': 'List'}, {'default': True, 'description': 'When false, the result will have a NULL geometry.', 'name': 'retainGeometry', 'optional': True, 'type': 'Boolean'}], 'description': 'Selects properties from a feature by name or RE2-compatible regex and optionally renames them.', 'returns': 'Element', 'type': 'Algorithm', 'hidden': False, 'name': 'Feature.select'})
# Feature.setGeometry
# Returns the feature, with the geometry replaced by the specified geometry.
#
# Args:
#   feature: The feature on which to set the geometry.
#   geometry: The geometry to set.
signatures.append({'args': [{'description': 'The feature on which to set the geometry.', 'name': 'feature', 'type': 'Element'}, {'default': None, 'description': 'The geometry to set.', 'name': 'geometry', 'optional': True, 'type': 'Geometry'}], 'description': 'Returns the feature, with the geometry replaced by the specified geometry.', 'returns': 'Element', 'type': 'Algorithm', 'hidden': False, 'name': 'Feature.setGeometry'})
# Feature.simplify
# Simplifies the geometry of a feature to within a given error margin. Note
# that this does not respect the error margin requested by the consumer of
# this algorithm, unless maxError is explicitly specified to be null. This
# overrides the default Earth Engine policy for propagating error margins, so
# regardless of the geometry accuracy requested from the output, the inputs
# will be requested with the error margin specified in the arguments to this
# algorithm. This results in consistent rendering at all zoom levels of a
# rendered vector map, but at lower zoom levels (i.e. zoomed out), the
# geometry won't be simplified, which may harm performance.
#
# Args:
#   feature: The feature whose geometry is being simplified.
#   maxError: The maximum amount of error by which the result may
#       differ from the input.
#   proj: If specified, the result will be in this projection.
#       Otherwise it will be in the same projection as the input. If
#       the error margin is in projected units, the margin will be
#       interpreted as units of this projection
signatures.append({'args': [{'description': 'The feature whose geometry is being simplified.', 'name': 'feature', 'type': 'Element'}, {'description': 'The maximum amount of error by which the result may differ from the input.', 'name': 'maxError', 'type': 'ErrorMargin'}, {'default': None, 'description': 'If specified, the result will be in this projection. Otherwise it will be in the same projection as the input. If the error margin is in projected units, the margin will be interpreted as units of this projection', 'name': 'proj', 'optional': True, 'type': 'Projection'}], 'description': "Simplifies the geometry of a feature to within a given error margin. Note that this does not respect the error margin requested by the consumer of this algorithm, unless maxError is explicitly specified to be null.\nThis overrides the default Earth Engine policy for propagating error margins, so regardless of the geometry accuracy requested from the output, the inputs will be requested with the error margin specified in the arguments to this algorithm. This results in consistent rendering at all zoom levels of a rendered vector map, but at lower zoom levels (i.e. zoomed out), the geometry won't be simplified, which may harm performance.", 'returns': 'Feature', 'type': 'Algorithm', 'hidden': False, 'name': 'Feature.simplify'})
# Feature.snap
# Snaps the vertices of the default geometry to a regular cell grid with
# radius near but less than the given snap radius in meters. Snapping can
# reduce the number of vertices, close gaps in adjacent spatial features, and
# push degenerate elements to lower dimensional objects, e.g. a narrow
# polygon may collapse to a line. When applied to a GeometryCollection,
# overlap created between different elements is not removed.
#
# Args:
#   feature: The feature whose geometry is being snapped.
#   snapRadius: The max distance to move vertices during
#       snapping. If in meters, 'proj' must not be specified,
#       otherwise if in units, 'proj' must specified.
#   proj: If unspecified the result will be in WGS84 with geodesic
#       edges and the snap radius must be in meters, otherwise the
#       snap radius must be in units and the result will be in this
#       projection with planar edges.
signatures.append({'args': [{'description': 'The feature whose geometry is being snapped.', 'name': 'feature', 'type': 'Element'}, {'description': "The max distance to move vertices during snapping. If in meters, 'proj' must not be specified, otherwise if in units, 'proj' must specified.", 'name': 'snapRadius', 'type': 'ErrorMargin'}, {'default': None, 'description': 'If unspecified the result will be in WGS84 with geodesic edges and the snap radius must be in meters, otherwise the snap radius must be in units and the result will be in this projection with planar edges.', 'name': 'proj', 'optional': True, 'type': 'Projection'}], 'description': 'Snaps the vertices of the default geometry to a regular cell grid with radius near but less than the given snap radius in meters. Snapping can reduce the number of vertices, close gaps in adjacent spatial features, and push degenerate elements to lower dimensional objects, e.g. a narrow polygon may collapse to a line. When applied to a GeometryCollection, overlap created between different elements is not removed.', 'returns': 'Feature', 'type': 'Algorithm', 'hidden': False, 'name': 'Feature.snap'})
# Feature.symmetricDifference
# Returns a feature containing the symmetric difference between geometries of
# two features.
#
# Args:
#   left: The feature containing the geometry used as the left
#       operand of the operation. The properties of the result will
#       be copied from this object.
#   right: The feature containing the geometry used as the right
#       operand of the operation. The properties of this object are
#       ignored.
#   maxError: The maximum amount of error tolerated when
#       performing any necessary reprojection.
#   proj: The projection in which to perform the operation. If not
#       specified, the operation will be performed in a spherical
#       coordinate system, and linear distances will be in meters on
#       the sphere.
signatures.append({'args': [{'description': 'The feature containing the geometry used as the left operand of the operation. The properties of the result will be copied from this object.', 'name': 'left', 'type': 'Element'}, {'description': 'The feature containing the geometry used as the right operand of the operation. The properties of this object are ignored.', 'name': 'right', 'type': 'Element'}, {'default': None, 'description': 'The maximum amount of error tolerated when performing any necessary reprojection.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}, {'default': None, 'description': 'The projection in which to perform the operation. If not specified, the operation will be performed in a spherical coordinate system, and linear distances will be in meters on the sphere.', 'name': 'proj', 'optional': True, 'type': 'Projection'}], 'description': 'Returns a feature containing the symmetric difference between geometries of two features.', 'returns': 'Feature', 'type': 'Algorithm', 'hidden': False, 'name': 'Feature.symmetricDifference'})
# Feature.toArray
# Creates an array from the given properties of an object, which must all be
# numbers.
#
# Args:
#   feature: The object from which to select array properties.
#   properties: The property selectors for each array element.
signatures.append({'args': [{'description': 'The object from which to select array properties.', 'name': 'feature', 'type': 'Feature'}, {'description': 'The property selectors for each array element.', 'name': 'properties', 'type': 'List'}], 'description': 'Creates an array from the given properties of an object, which must all be numbers.', 'returns': 'Array', 'type': 'Algorithm', 'hidden': False, 'name': 'Feature.toArray'})
# Feature.transform
# Transforms the geometry of a feature to a specific projection.
#
# Args:
#   feature: The feature the geometry of which is being converted.
#   proj: The target projection. Defaults to WGS84. If this has a
#       geographic CRS, the edges of the geometry will be interpreted
#       as geodesics. Otherwise they will be interpreted as straight
#       lines in the projection.
#   maxError: The maximum projection error.
signatures.append({'args': [{'description': 'The feature the geometry of which is being converted.', 'name': 'feature', 'type': 'Element'}, {'default': {'crs': 'EPSG:4326', 'transform': [1.0, 0.0, 0.0, 0.0, 1.0, 0.0], 'type': 'Projection'}, 'description': 'The target projection. Defaults to WGS84. If this has a geographic CRS, the edges of the geometry will be interpreted as geodesics. Otherwise they will be interpreted as straight lines in the projection.', 'name': 'proj', 'optional': True, 'type': 'Projection'}, {'default': None, 'description': 'The maximum projection error.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}], 'description': 'Transforms the geometry of a feature to a specific projection.', 'returns': 'Feature', 'type': 'Algorithm', 'hidden': False, 'name': 'Feature.transform'})
# Feature.union
# Returns a feature containing the union of the geometries of two features.
#
# Args:
#   left: The feature containing the geometry used as the left
#       operand of the operation. The properties of the result will
#       be copied from this object.
#   right: The feature containing the geometry used as the right
#       operand of the operation. The properties of this object are
#       ignored.
#   maxError: The maximum amount of error tolerated when
#       performing any necessary reprojection.
#   proj: The projection in which to perform the operation. If not
#       specified, the operation will be performed in a spherical
#       coordinate system, and linear distances will be in meters on
#       the sphere.
signatures.append({'args': [{'description': 'The feature containing the geometry used as the left operand of the operation. The properties of the result will be copied from this object.', 'name': 'left', 'type': 'Element'}, {'description': 'The feature containing the geometry used as the right operand of the operation. The properties of this object are ignored.', 'name': 'right', 'type': 'Element'}, {'default': None, 'description': 'The maximum amount of error tolerated when performing any necessary reprojection.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}, {'default': None, 'description': 'The projection in which to perform the operation. If not specified, the operation will be performed in a spherical coordinate system, and linear distances will be in meters on the sphere.', 'name': 'proj', 'optional': True, 'type': 'Projection'}], 'description': 'Returns a feature containing the union of the geometries of two features.', 'returns': 'Feature', 'type': 'Algorithm', 'hidden': False, 'name': 'Feature.union'})
# Feature.withinDistance
# Returns true iff the geometries of two features are within a specified
# distance.
#
# Args:
#   left: The feature containing the geometry used as the left
#       operand of the operation.
#   right: The feature containing the geometry used as the right
#       operand of the operation.
#   distance: The distance threshold. If a projection is
#       specified, the distance is in units of that projected
#       coordinate system, otherwise it is in meters.
#   maxError: The maximum amount of error tolerated when
#       performing any necessary reprojection.
#   proj: The projection in which to perform the operation. If not
#       specified, the operation will be performed in a spherical
#       coordinate system, and linear distances will be in meters on
#       the sphere.
signatures.append({'args': [{'description': 'The feature containing the geometry used as the left operand of the operation.', 'name': 'left', 'type': 'Element'}, {'description': 'The feature containing the geometry used as the right operand of the operation.', 'name': 'right', 'type': 'Element'}, {'description': 'The distance threshold. If a projection is specified, the distance is in units of that projected coordinate system, otherwise it is in meters.', 'name': 'distance', 'type': 'Float'}, {'default': None, 'description': 'The maximum amount of error tolerated when performing any necessary reprojection.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}, {'default': None, 'description': 'The projection in which to perform the operation. If not specified, the operation will be performed in a spherical coordinate system, and linear distances will be in meters on the sphere.', 'name': 'proj', 'optional': True, 'type': 'Projection'}], 'description': 'Returns true iff the geometries of two features are within a specified distance.', 'returns': 'Boolean', 'type': 'Algorithm', 'hidden': False, 'name': 'Feature.withinDistance'})
# FeatureCollection.classify
# Classifies each feature in a collection.
#
# Args:
#   features: The collection of features to classify. Each
#       feature must contain all the properties in the
#       classifier's schema.
#   classifier: The classifier to use.
#   outputName: The name of the output property to be added.
signatures.append({'args': [{'description': "The collection of features to classify. Each feature must contain all the properties in the classifier's schema.", 'name': 'features', 'type': 'FeatureCollection'}, {'description': 'The classifier to use.', 'name': 'classifier', 'type': 'Object'}, {'default': 'classification', 'description': 'The name of the output property to be added.', 'name': 'outputName', 'optional': True, 'type': 'String'}], 'description': 'Classifies each feature in a collection.', 'returns': 'FeatureCollection', 'type': 'Algorithm', 'hidden': False, 'name': 'FeatureCollection.classify'})
# FeatureCollection.cluster
# Clusters each feature in a collection, adding a new column to each feature
# containing the cluster number to which it has been assigned.
#
# Args:
#   features: The collection of features to cluster. Each feature
#       must contain all the properties in the clusterer's
#       schema.
#   clusterer: The clusterer to use.
#   outputName: The name of the output property to be added.
signatures.append({'args': [{'description': "The collection of features to cluster. Each feature must contain all the properties in the clusterer's schema.", 'name': 'features', 'type': 'FeatureCollection'}, {'description': 'The clusterer to use.', 'name': 'clusterer', 'type': 'Clusterer'}, {'default': 'cluster', 'description': 'The name of the output property to be added.', 'name': 'outputName', 'optional': True, 'type': 'String'}], 'description': 'Clusters each feature in a collection, adding a new column to each feature containing the cluster number to which it has been assigned.', 'returns': 'FeatureCollection', 'type': 'Algorithm', 'hidden': False, 'name': 'FeatureCollection.cluster'})
# FeatureCollection.inverseDistance
# Returns an inverse-distance weighted estimate of the value at each pixel.
#
# Args:
#   collection: Feature collection to use as source data for
#       the estimation.
#   range: Size of the interpolation window (in meters).
#   propertyName: Name of the numeric property to be
#       estimated.
#   mean: Global expected mean.
#   stdDev: Global standard deviation.
#   gamma: Determines how quickly the estimates tend towards the
#       global mean.
#   reducer: Reducer used to collapse the 'propertyName' value of
#       overlapping points into a single value.
signatures.append({'args': [{'description': 'Feature collection to use as source data for the estimation.', 'name': 'collection', 'type': 'FeatureCollection'}, {'description': 'Size of the interpolation window (in meters).', 'name': 'range', 'type': 'Float'}, {'description': 'Name of the numeric property to be estimated.', 'name': 'propertyName', 'type': 'String'}, {'description': 'Global expected mean.', 'name': 'mean', 'type': 'Float'}, {'description': 'Global standard deviation.', 'name': 'stdDev', 'type': 'Float'}, {'default': 1.0, 'description': 'Determines how quickly the estimates tend towards the global mean.', 'name': 'gamma', 'optional': True, 'type': 'Float'}, {'default': None, 'description': "Reducer used to collapse the 'propertyName' value of overlapping points into a single value.", 'name': 'reducer', 'optional': True, 'type': 'Reducer'}], 'description': 'Returns an inverse-distance weighted estimate of the value at each pixel.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'FeatureCollection.inverseDistance'})
# FeatureCollection.kriging
# Returns the results of sampling a Kriging estimator at each pixel.
#
# Args:
#   collection: Feature collection to use as source data for
#       the estimation.
#   propertyName: Property to be estimated (must be numeric).
#   shape: Semivariogram shape (one of {exponential, gaussian,
#       spherical}).
#   range: Semivariogram range.
#   sill: Semivariogram sill.
#   nugget: Semivariogram nugget.
#   maxDistance: Radius which determines which features are
#       included in each pixel's computation. Defaults to the
#       semivariogram's range.
#   reducer: Reducer used to collapse the 'propertyName' value of
#       overlapping points into a single value.
signatures.append({'args': [{'description': 'Feature collection to use as source data for the estimation.', 'name': 'collection', 'type': 'FeatureCollection'}, {'description': 'Property to be estimated (must be numeric).', 'name': 'propertyName', 'type': 'String'}, {'description': 'Semivariogram shape (one of {exponential, gaussian, spherical}).', 'name': 'shape', 'type': 'String'}, {'description': 'Semivariogram range.', 'name': 'range', 'type': 'Float'}, {'description': 'Semivariogram sill.', 'name': 'sill', 'type': 'Float'}, {'description': 'Semivariogram nugget.', 'name': 'nugget', 'type': 'Float'}, {'default': None, 'description': "Radius which determines which features are included in each pixel's computation. Defaults to the semivariogram's range.", 'name': 'maxDistance', 'optional': True, 'type': 'Float'}, {'default': None, 'description': "Reducer used to collapse the 'propertyName' value of overlapping points into a single value.", 'name': 'reducer', 'optional': True, 'type': 'Reducer'}], 'description': 'Returns the results of sampling a Kriging estimator at each pixel.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'FeatureCollection.kriging'})
# FeatureCollection.makeArray
# Add a 1-D Array to each feature in a collection by combining a list of
# properties for each feature into a 1-D Array. All of the properties must be
# numeric values.  If a feature doesn't contain all of the named properties,
# or any of them aren't numeric, the feature will be dropped from the
# resulting collection.
#
# Args:
#   collection: The input collection from which properties will
#       be selected.
#   properties: The properties to select.
#   name: The name of the new array property.
signatures.append({'args': [{'description': 'The input collection from which properties will be selected.', 'name': 'collection', 'type': 'FeatureCollection'}, {'description': 'The properties to select.', 'name': 'properties', 'type': 'List'}, {'default': 'array', 'description': 'The name of the new array property.', 'name': 'name', 'optional': True, 'type': 'String'}], 'description': "Add a 1-D Array to each feature in a collection by combining a list of properties for each feature into a 1-D Array. All of the properties must be numeric values.  If a feature doesn't contain all of the named properties, or any of them aren't numeric, the feature will be dropped from the resulting collection.", 'returns': 'FeatureCollection', 'type': 'Algorithm', 'hidden': False, 'name': 'FeatureCollection.makeArray'})
# FeatureCollection.randomPoints
# Generates points that are uniformly random on the sphere, and within the
# given region.
#
# Args:
#   region: The region to generate points for.
#   points: The number of points to generate.
#   seed: A seed for the random number generator.
#   maxError: The maximum amount of error tolerated when
#       performing any necessary reprojection.
signatures.append({'args': [{'description': 'The region to generate points for.', 'name': 'region', 'type': 'Geometry'}, {'default': 1000, 'description': 'The number of points to generate.', 'name': 'points', 'optional': True, 'type': 'Integer'}, {'default': 0, 'description': 'A seed for the random number generator.', 'name': 'seed', 'optional': True, 'type': 'Long'}, {'default': {'type': 'ErrorMargin', 'unit': 'meters', 'value': 100.0}, 'description': 'The maximum amount of error tolerated when performing any necessary reprojection.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}], 'description': 'Generates points that are uniformly random on the sphere, and within the given region.', 'returns': 'FeatureCollection', 'type': 'Algorithm', 'hidden': False, 'name': 'FeatureCollection.randomPoints'})
# FeatureCollection.trainClassifier
# Trains a classifier from features in a collection, using the specified
# numeric properties of each feature as training data.  The input data is
# specified with the collection  and property_list arguments.  The input is
# generated by extracting the specified properties from each feature in the
# collection. The list of properties should not include the class_property,
# as it is handled separately.  The classifier will expect future inputs to
# be classified to be in the same order.  To use the classifier library,
# specify the classifier_name, classifier_parameters, and classifier_mode
# arguments.  To enable cross-validation or bagging, set the num_subsamples
# argument. When bagging, set the bootstrap_subsampling factor and the
# bootstrap_aggregator as well.  To use a custom classifier, specify it using
# the classifier parameter.
#
# Args:
#   collection: A collection of classified features to use for
#       supervised classification.
#   property_list: The list of properties in each element of
#       training_features to include in the training input.
#   class_property: The name of the property in each
#       element of training_features containing its class
#       number.
#   classifier_name: The name of the Abe classifier to
#       use. Currently supported values are
#       FastNaiveBayes, GmoMaxEnt, Winnow,
#       MultiClassPerceptron, Pegasos, Cart,
#       RifleSerialClassifier, IKPamir, VotingSvm,
#       MarginSvm, ContinuousNaiveBayes. Ignored if a
#       classifier argument is provided.
#   classifier_parameters: The Abe classifier
#       parameters. Ignored if a classifier argument
#       is provided.
#   classifier_mode: The classifier mode. Accepted values
#       are 'classification', 'regression' and
#       'probability'. Ignored if a classifier argument is
#       provided.
#   num_subsamples: The number of subsamples to use for
#       cross-validation or bagging. If 1, no cross-
#       validation or bagging is performed. Ignored if a
#       classifier argument is provided.
#   bootstrap_subsampling: The bootstrap subsampling
#       factor. Ignored if a classifier argument is
#       provided.
#   bootstrap_aggregator: The bootstrap aggregator.
#       Ignored if a classifier argument is provided.
#   classifier: A pre-built classifier to use.
signatures.append({'args': [{'description': 'A collection of classified features to use for supervised classification.', 'name': 'collection', 'type': 'FeatureCollection'}, {'default': None, 'description': 'The list of properties in each element of training_features to include in the training input.', 'name': 'property_list', 'optional': True, 'type': 'List'}, {'default': 'classification', 'description': 'The name of the property in each element of training_features containing its class number.', 'name': 'class_property', 'optional': True, 'type': 'String'}, {'default': 'FastNaiveBayes', 'description': 'The name of the Abe classifier to use. Currently supported values are FastNaiveBayes, GmoMaxEnt, Winnow, MultiClassPerceptron, Pegasos, Cart, RifleSerialClassifier, IKPamir, VotingSvm, MarginSvm, ContinuousNaiveBayes. Ignored if a classifier argument is provided.', 'name': 'classifier_name', 'optional': True, 'type': 'String'}, {'default': '', 'description': 'The Abe classifier parameters. Ignored if a classifier argument is provided.', 'name': 'classifier_parameters', 'optional': True, 'type': 'String'}, {'default': 'classification', 'description': "The classifier mode. Accepted values are 'classification', 'regression' and 'probability'. Ignored if a classifier argument is provided.", 'name': 'classifier_mode', 'optional': True, 'type': 'String'}, {'default': 1, 'description': 'The number of subsamples to use for cross-validation or bagging. If 1, no cross-validation or bagging is performed. Ignored if a classifier argument is provided.', 'name': 'num_subsamples', 'optional': True, 'type': 'Integer'}, {'default': None, 'description': 'The bootstrap subsampling factor. Ignored if a classifier argument is provided.', 'name': 'bootstrap_subsampling', 'optional': True, 'type': 'Float'}, {'default': None, 'description': 'The bootstrap aggregator. Ignored if a classifier argument is provided.', 'name': 'bootstrap_aggregator', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'A pre-built classifier to use.', 'name': 'classifier', 'optional': True, 'type': 'OldClassifier'}], 'description': 'Trains a classifier from features in a collection, using the specified numeric properties of each feature as training data.\n\nThe input data is specified with the collection  and property_list arguments.  The input is generated by extracting the specified properties from each feature in the collection. The list of properties should not include the class_property, as it is handled separately.  The classifier will expect future inputs to be classified to be in the same order.\n\nTo use the classifier library, specify the classifier_name, classifier_parameters, and classifier_mode arguments.\n\nTo enable cross-validation or bagging, set the num_subsamples argument. When bagging, set the bootstrap_subsampling factor and the bootstrap_aggregator as well.\n\nTo use a custom classifier, specify it using the classifier parameter.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': True, 'deprecated': 'Use Classifier.train().', 'name': 'FeatureCollection.trainClassifier'})
# Filter.always
# Simple filter ALWAYS.
signatures.append({'args': [], 'description': 'Simple filter ALWAYS.', 'returns': 'Filter', 'type': 'Algorithm', 'hidden': True, 'name': 'Filter.always'})
# Filter.and
# Returns a filter that passes if each of the component filters pass.
#
# Args:
#   filters: The filters to conjunct.
signatures.append({'args': [{'description': 'The filters to conjunct.', 'name': 'filters', 'type': 'List'}], 'description': 'Returns a filter that passes if each of the component filters pass.', 'returns': 'Filter', 'type': 'Algorithm', 'hidden': False, 'name': 'Filter.and'})
# Filter.calendarRange
# Returns a filter that passes if the object's timestamp falls within the
# given range of a calendar field.  The month, day_of_year, day_of_month, and
# day_of_week are 1-based.  Times are assumed to be in UTC.  Weeks are
# assumed to begin on Monday as day 1.   If end < start then this tests for
# value >= start OR value <= end, to allow for wrapping.
#
# Args:
#   start: The start of the desired calendar field, inclusive.
#   end: The end of the desired calendar field, inclusive. Defaults to
#       the same value as start.
#   field: The calendar field to filter over. Options are: 'year',
#       'month', 'hour', 'minute', 'day_of_year', 'day_of_month',
#       and 'day_of_week'.
signatures.append({'args': [{'description': 'The start of the desired calendar field, inclusive.', 'name': 'start', 'type': 'Integer'}, {'default': None, 'description': 'The end of the desired calendar field, inclusive. Defaults to the same value as start.', 'name': 'end', 'optional': True, 'type': 'Integer'}, {'default': 'day_of_year', 'description': "The calendar field to filter over. Options are: 'year', 'month', 'hour', 'minute', 'day_of_year', 'day_of_month', and 'day_of_week'.", 'name': 'field', 'optional': True, 'type': 'String'}], 'description': "Returns a filter that passes if the object's timestamp falls within the given range of a calendar field.  The month, day_of_year, day_of_month, and day_of_week are 1-based.  Times are assumed to be in UTC.  Weeks are assumed to begin on Monday as day 1.   If end < start then this tests for value >= start OR value <= end, to allow for wrapping.", 'returns': 'Filter', 'type': 'Algorithm', 'hidden': False, 'name': 'Filter.calendarRange'})
# Filter.contains
# Creates a unary or binary filter that passes if the left geometry contains
# the right geometry (empty geometries are not contained in anything).
#
# Args:
#   leftField: A selector for the left operand. Should not be
#       specified if leftValue is specified.
#   rightValue: The value of the right operand. Should not be
#       specified if rightField is specified.
#   rightField: A selector for the right operand. Should not be
#       specified if rightValue is specified.
#   leftValue: The value of the left operand. Should not be
#       specified if leftField is specified.
#   maxError: The maximum reprojection error allowed during
#       filter application.
signatures.append({'args': [{'default': None, 'description': 'A selector for the left operand. Should not be specified if leftValue is specified.', 'name': 'leftField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the right operand. Should not be specified if rightField is specified.', 'name': 'rightValue', 'optional': True, 'type': 'Object'}, {'default': None, 'description': 'A selector for the right operand. Should not be specified if rightValue is specified.', 'name': 'rightField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the left operand. Should not be specified if leftField is specified.', 'name': 'leftValue', 'optional': True, 'type': 'Object'}, {'default': {'type': 'ErrorMargin', 'unit': 'meters', 'value': 0.1}, 'description': 'The maximum reprojection error allowed during filter application.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}], 'description': 'Creates a unary or binary filter that passes if the left geometry contains the right geometry (empty geometries are not contained in anything).', 'returns': 'Filter', 'type': 'Algorithm', 'hidden': False, 'name': 'Filter.contains'})
# Filter.dateRangeContains
# Creates a unary or binary filter that passes if the left operand, a date
# range, contains the right operand, a date.
#
# Args:
#   leftField: A selector for the left operand. Should not be
#       specified if leftValue is specified.
#   rightValue: The value of the right operand. Should not be
#       specified if rightField is specified.
#   rightField: A selector for the right operand. Should not be
#       specified if rightValue is specified.
#   leftValue: The value of the left operand. Should not be
#       specified if leftField is specified.
signatures.append({'args': [{'default': None, 'description': 'A selector for the left operand. Should not be specified if leftValue is specified.', 'name': 'leftField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the right operand. Should not be specified if rightField is specified.', 'name': 'rightValue', 'optional': True, 'type': 'Object'}, {'default': None, 'description': 'A selector for the right operand. Should not be specified if rightValue is specified.', 'name': 'rightField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the left operand. Should not be specified if leftField is specified.', 'name': 'leftValue', 'optional': True, 'type': 'Object'}], 'description': 'Creates a unary or binary filter that passes if the left operand, a date range, contains the right operand, a date.', 'returns': 'Filter', 'type': 'Algorithm', 'hidden': False, 'name': 'Filter.dateRangeContains'})
# Filter.dayOfYear
# Returns a filter that passes if the object's timestamp falls within the
# given day-of-year range.
#
# Args:
#   start: The start of the desired day range, inclusive.
#   end: The end of the desired day range, exclusive.
signatures.append({'args': [{'description': 'The start of the desired day range, inclusive.', 'name': 'start', 'type': 'Integer'}, {'description': 'The end of the desired day range, exclusive.', 'name': 'end', 'type': 'Integer'}], 'description': "Returns a filter that passes if the object's timestamp falls within the given day-of-year range.", 'returns': 'Filter', 'type': 'Algorithm', 'hidden': False, 'name': 'Filter.dayOfYear'})
# Filter.disjoint
# Creates a unary or binary filter that passes unless the left geometry
# intersects the right geometry.
#
# Args:
#   leftField: A selector for the left operand. Should not be
#       specified if leftValue is specified.
#   rightValue: The value of the right operand. Should not be
#       specified if rightField is specified.
#   rightField: A selector for the right operand. Should not be
#       specified if rightValue is specified.
#   leftValue: The value of the left operand. Should not be
#       specified if leftField is specified.
#   maxError: The maximum reprojection error allowed during
#       filter application.
signatures.append({'args': [{'default': None, 'description': 'A selector for the left operand. Should not be specified if leftValue is specified.', 'name': 'leftField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the right operand. Should not be specified if rightField is specified.', 'name': 'rightValue', 'optional': True, 'type': 'Object'}, {'default': None, 'description': 'A selector for the right operand. Should not be specified if rightValue is specified.', 'name': 'rightField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the left operand. Should not be specified if leftField is specified.', 'name': 'leftValue', 'optional': True, 'type': 'Object'}, {'default': {'type': 'ErrorMargin', 'unit': 'meters', 'value': 0.1}, 'description': 'The maximum reprojection error allowed during filter application.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}], 'description': 'Creates a unary or binary filter that passes unless the left geometry intersects the right geometry.', 'returns': 'Filter', 'type': 'Algorithm', 'hidden': False, 'name': 'Filter.disjoint'})
# Filter.eq
# Creates a unary or binary filter that passes if the two operands are
# equals.
#
# Args:
#   leftField: A selector for the left operand. Should not be
#       specified if leftValue is specified.
#   rightValue: The value of the right operand. Should not be
#       specified if rightField is specified.
#   rightField: A selector for the right operand. Should not be
#       specified if rightValue is specified.
#   leftValue: The value of the left operand. Should not be
#       specified if leftField is specified.
signatures.append({'args': [{'default': None, 'description': 'A selector for the left operand. Should not be specified if leftValue is specified.', 'name': 'leftField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the right operand. Should not be specified if rightField is specified.', 'name': 'rightValue', 'optional': True, 'type': 'Object'}, {'default': None, 'description': 'A selector for the right operand. Should not be specified if rightValue is specified.', 'name': 'rightField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the left operand. Should not be specified if leftField is specified.', 'name': 'leftValue', 'optional': True, 'type': 'Object'}], 'description': 'Creates a unary or binary filter that passes if the two operands are equals.', 'returns': 'Filter', 'type': 'Algorithm', 'hidden': False, 'name': 'Filter.eq'})
# Filter.equals
# Creates a unary or binary filter that passes if the two operands are
# equals.
#
# Args:
#   leftField: A selector for the left operand. Should not be
#       specified if leftValue is specified.
#   rightValue: The value of the right operand. Should not be
#       specified if rightField is specified.
#   rightField: A selector for the right operand. Should not be
#       specified if rightValue is specified.
#   leftValue: The value of the left operand. Should not be
#       specified if leftField is specified.
signatures.append({'args': [{'default': None, 'description': 'A selector for the left operand. Should not be specified if leftValue is specified.', 'name': 'leftField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the right operand. Should not be specified if rightField is specified.', 'name': 'rightValue', 'optional': True, 'type': 'Object'}, {'default': None, 'description': 'A selector for the right operand. Should not be specified if rightValue is specified.', 'name': 'rightField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the left operand. Should not be specified if leftField is specified.', 'name': 'leftValue', 'optional': True, 'type': 'Object'}], 'description': 'Creates a unary or binary filter that passes if the two operands are equals.', 'returns': 'Filter', 'type': 'Algorithm', 'hidden': False, 'name': 'Filter.equals'})
# Filter.greaterThan
# Creates a unary or binary filter that passes if the left operand is greater
# than the right operand.
#
# Args:
#   leftField: A selector for the left operand. Should not be
#       specified if leftValue is specified.
#   rightValue: The value of the right operand. Should not be
#       specified if rightField is specified.
#   rightField: A selector for the right operand. Should not be
#       specified if rightValue is specified.
#   leftValue: The value of the left operand. Should not be
#       specified if leftField is specified.
signatures.append({'args': [{'default': None, 'description': 'A selector for the left operand. Should not be specified if leftValue is specified.', 'name': 'leftField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the right operand. Should not be specified if rightField is specified.', 'name': 'rightValue', 'optional': True, 'type': 'Object'}, {'default': None, 'description': 'A selector for the right operand. Should not be specified if rightValue is specified.', 'name': 'rightField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the left operand. Should not be specified if leftField is specified.', 'name': 'leftValue', 'optional': True, 'type': 'Object'}], 'description': 'Creates a unary or binary filter that passes if the left operand is greater than the right operand.', 'returns': 'Filter', 'type': 'Algorithm', 'hidden': False, 'name': 'Filter.greaterThan'})
# Filter.greaterThanOrEquals
# Creates a unary or binary filter that passes unless the left operand is
# less than the right operand.
#
# Args:
#   leftField: A selector for the left operand. Should not be
#       specified if leftValue is specified.
#   rightValue: The value of the right operand. Should not be
#       specified if rightField is specified.
#   rightField: A selector for the right operand. Should not be
#       specified if rightValue is specified.
#   leftValue: The value of the left operand. Should not be
#       specified if leftField is specified.
signatures.append({'args': [{'default': None, 'description': 'A selector for the left operand. Should not be specified if leftValue is specified.', 'name': 'leftField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the right operand. Should not be specified if rightField is specified.', 'name': 'rightValue', 'optional': True, 'type': 'Object'}, {'default': None, 'description': 'A selector for the right operand. Should not be specified if rightValue is specified.', 'name': 'rightField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the left operand. Should not be specified if leftField is specified.', 'name': 'leftValue', 'optional': True, 'type': 'Object'}], 'description': 'Creates a unary or binary filter that passes unless the left operand is less than the right operand.', 'returns': 'Filter', 'type': 'Algorithm', 'hidden': False, 'name': 'Filter.greaterThanOrEquals'})
# Filter.gt
# Creates a unary or binary filter that passes if the left operand is greater
# than the right operand.
#
# Args:
#   leftField: A selector for the left operand. Should not be
#       specified if leftValue is specified.
#   rightValue: The value of the right operand. Should not be
#       specified if rightField is specified.
#   rightField: A selector for the right operand. Should not be
#       specified if rightValue is specified.
#   leftValue: The value of the left operand. Should not be
#       specified if leftField is specified.
signatures.append({'args': [{'default': None, 'description': 'A selector for the left operand. Should not be specified if leftValue is specified.', 'name': 'leftField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the right operand. Should not be specified if rightField is specified.', 'name': 'rightValue', 'optional': True, 'type': 'Object'}, {'default': None, 'description': 'A selector for the right operand. Should not be specified if rightValue is specified.', 'name': 'rightField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the left operand. Should not be specified if leftField is specified.', 'name': 'leftValue', 'optional': True, 'type': 'Object'}], 'description': 'Creates a unary or binary filter that passes if the left operand is greater than the right operand.', 'returns': 'Filter', 'type': 'Algorithm', 'hidden': False, 'name': 'Filter.gt'})
# Filter.gte
# Creates a unary or binary filter that passes unless the left operand is
# less than the right operand.
#
# Args:
#   leftField: A selector for the left operand. Should not be
#       specified if leftValue is specified.
#   rightValue: The value of the right operand. Should not be
#       specified if rightField is specified.
#   rightField: A selector for the right operand. Should not be
#       specified if rightValue is specified.
#   leftValue: The value of the left operand. Should not be
#       specified if leftField is specified.
signatures.append({'args': [{'default': None, 'description': 'A selector for the left operand. Should not be specified if leftValue is specified.', 'name': 'leftField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the right operand. Should not be specified if rightField is specified.', 'name': 'rightValue', 'optional': True, 'type': 'Object'}, {'default': None, 'description': 'A selector for the right operand. Should not be specified if rightValue is specified.', 'name': 'rightField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the left operand. Should not be specified if leftField is specified.', 'name': 'leftValue', 'optional': True, 'type': 'Object'}], 'description': 'Creates a unary or binary filter that passes unless the left operand is less than the right operand.', 'returns': 'Filter', 'type': 'Algorithm', 'hidden': False, 'name': 'Filter.gte'})
# Filter.hasGeometry
# Simple filter HAS_GEOMETRY.
signatures.append({'args': [], 'description': 'Simple filter HAS_GEOMETRY.', 'returns': 'Filter', 'type': 'Algorithm', 'hidden': True, 'name': 'Filter.hasGeometry'})
# Filter.inList
# Creates a unary or binary filter that passes if the left operand, a list,
# contains the right operand.
#
# Args:
#   leftField: A selector for the left operand. Should not be
#       specified if leftValue is specified.
#   rightValue: The value of the right operand. Should not be
#       specified if rightField is specified.
#   rightField: A selector for the right operand. Should not be
#       specified if rightValue is specified.
#   leftValue: The value of the left operand. Should not be
#       specified if leftField is specified.
signatures.append({'args': [{'default': None, 'description': 'A selector for the left operand. Should not be specified if leftValue is specified.', 'name': 'leftField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the right operand. Should not be specified if rightField is specified.', 'name': 'rightValue', 'optional': True, 'type': 'Object'}, {'default': None, 'description': 'A selector for the right operand. Should not be specified if rightValue is specified.', 'name': 'rightField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the left operand. Should not be specified if leftField is specified.', 'name': 'leftValue', 'optional': True, 'type': 'Object'}], 'description': 'Creates a unary or binary filter that passes if the left operand, a list, contains the right operand.', 'returns': 'Filter', 'type': 'Algorithm', 'hidden': False, 'name': 'Filter.inList'})
# Filter.intersects
# Creates a unary or binary filter that passes if the left geometry
# intersects the right geometry.
#
# Args:
#   leftField: A selector for the left operand. Should not be
#       specified if leftValue is specified.
#   rightValue: The value of the right operand. Should not be
#       specified if rightField is specified.
#   rightField: A selector for the right operand. Should not be
#       specified if rightValue is specified.
#   leftValue: The value of the left operand. Should not be
#       specified if leftField is specified.
#   maxError: The maximum reprojection error allowed during
#       filter application.
signatures.append({'args': [{'default': None, 'description': 'A selector for the left operand. Should not be specified if leftValue is specified.', 'name': 'leftField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the right operand. Should not be specified if rightField is specified.', 'name': 'rightValue', 'optional': True, 'type': 'Object'}, {'default': None, 'description': 'A selector for the right operand. Should not be specified if rightValue is specified.', 'name': 'rightField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the left operand. Should not be specified if leftField is specified.', 'name': 'leftValue', 'optional': True, 'type': 'Object'}, {'default': {'type': 'ErrorMargin', 'unit': 'meters', 'value': 0.1}, 'description': 'The maximum reprojection error allowed during filter application.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}], 'description': 'Creates a unary or binary filter that passes if the left geometry intersects the right geometry.', 'returns': 'Filter', 'type': 'Algorithm', 'hidden': False, 'name': 'Filter.intersects'})
# Filter.isContained
# Creates a unary or binary filter that passes if the right geometry contains
# the left geometry (empty geometries are not contained in anything).
#
# Args:
#   leftField: A selector for the left operand. Should not be
#       specified if leftValue is specified.
#   rightValue: The value of the right operand. Should not be
#       specified if rightField is specified.
#   rightField: A selector for the right operand. Should not be
#       specified if rightValue is specified.
#   leftValue: The value of the left operand. Should not be
#       specified if leftField is specified.
#   maxError: The maximum reprojection error allowed during
#       filter application.
signatures.append({'args': [{'default': None, 'description': 'A selector for the left operand. Should not be specified if leftValue is specified.', 'name': 'leftField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the right operand. Should not be specified if rightField is specified.', 'name': 'rightValue', 'optional': True, 'type': 'Object'}, {'default': None, 'description': 'A selector for the right operand. Should not be specified if rightValue is specified.', 'name': 'rightField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the left operand. Should not be specified if leftField is specified.', 'name': 'leftValue', 'optional': True, 'type': 'Object'}, {'default': {'type': 'ErrorMargin', 'unit': 'meters', 'value': 0.1}, 'description': 'The maximum reprojection error allowed during filter application.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}], 'description': 'Creates a unary or binary filter that passes if the right geometry contains the left geometry (empty geometries are not contained in anything).', 'returns': 'Filter', 'type': 'Algorithm', 'hidden': False, 'name': 'Filter.isContained'})
# Filter.lessThan
# Creates a unary or binary filter that passes if the left operand is less
# than the right operand.
#
# Args:
#   leftField: A selector for the left operand. Should not be
#       specified if leftValue is specified.
#   rightValue: The value of the right operand. Should not be
#       specified if rightField is specified.
#   rightField: A selector for the right operand. Should not be
#       specified if rightValue is specified.
#   leftValue: The value of the left operand. Should not be
#       specified if leftField is specified.
signatures.append({'args': [{'default': None, 'description': 'A selector for the left operand. Should not be specified if leftValue is specified.', 'name': 'leftField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the right operand. Should not be specified if rightField is specified.', 'name': 'rightValue', 'optional': True, 'type': 'Object'}, {'default': None, 'description': 'A selector for the right operand. Should not be specified if rightValue is specified.', 'name': 'rightField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the left operand. Should not be specified if leftField is specified.', 'name': 'leftValue', 'optional': True, 'type': 'Object'}], 'description': 'Creates a unary or binary filter that passes if the left operand is less than the right operand.', 'returns': 'Filter', 'type': 'Algorithm', 'hidden': False, 'name': 'Filter.lessThan'})
# Filter.lessThanOrEquals
# Creates a unary or binary filter that passes unless the left operand is
# greater than the right operand.
#
# Args:
#   leftField: A selector for the left operand. Should not be
#       specified if leftValue is specified.
#   rightValue: The value of the right operand. Should not be
#       specified if rightField is specified.
#   rightField: A selector for the right operand. Should not be
#       specified if rightValue is specified.
#   leftValue: The value of the left operand. Should not be
#       specified if leftField is specified.
signatures.append({'args': [{'default': None, 'description': 'A selector for the left operand. Should not be specified if leftValue is specified.', 'name': 'leftField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the right operand. Should not be specified if rightField is specified.', 'name': 'rightValue', 'optional': True, 'type': 'Object'}, {'default': None, 'description': 'A selector for the right operand. Should not be specified if rightValue is specified.', 'name': 'rightField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the left operand. Should not be specified if leftField is specified.', 'name': 'leftValue', 'optional': True, 'type': 'Object'}], 'description': 'Creates a unary or binary filter that passes unless the left operand is greater than the right operand.', 'returns': 'Filter', 'type': 'Algorithm', 'hidden': False, 'name': 'Filter.lessThanOrEquals'})
# Filter.listContains
# Creates a unary or binary filter that passes if the left operand, a list,
# contains the right operand.
#
# Args:
#   leftField: A selector for the left operand. Should not be
#       specified if leftValue is specified.
#   rightValue: The value of the right operand. Should not be
#       specified if rightField is specified.
#   rightField: A selector for the right operand. Should not be
#       specified if rightValue is specified.
#   leftValue: The value of the left operand. Should not be
#       specified if leftField is specified.
signatures.append({'args': [{'default': None, 'description': 'A selector for the left operand. Should not be specified if leftValue is specified.', 'name': 'leftField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the right operand. Should not be specified if rightField is specified.', 'name': 'rightValue', 'optional': True, 'type': 'Object'}, {'default': None, 'description': 'A selector for the right operand. Should not be specified if rightValue is specified.', 'name': 'rightField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the left operand. Should not be specified if leftField is specified.', 'name': 'leftValue', 'optional': True, 'type': 'Object'}], 'description': 'Creates a unary or binary filter that passes if the left operand, a list, contains the right operand.', 'returns': 'Filter', 'type': 'Algorithm', 'hidden': False, 'name': 'Filter.listContains'})
# Filter.lt
# Creates a unary or binary filter that passes if the left operand is less
# than the right operand.
#
# Args:
#   leftField: A selector for the left operand. Should not be
#       specified if leftValue is specified.
#   rightValue: The value of the right operand. Should not be
#       specified if rightField is specified.
#   rightField: A selector for the right operand. Should not be
#       specified if rightValue is specified.
#   leftValue: The value of the left operand. Should not be
#       specified if leftField is specified.
signatures.append({'args': [{'default': None, 'description': 'A selector for the left operand. Should not be specified if leftValue is specified.', 'name': 'leftField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the right operand. Should not be specified if rightField is specified.', 'name': 'rightValue', 'optional': True, 'type': 'Object'}, {'default': None, 'description': 'A selector for the right operand. Should not be specified if rightValue is specified.', 'name': 'rightField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the left operand. Should not be specified if leftField is specified.', 'name': 'leftValue', 'optional': True, 'type': 'Object'}], 'description': 'Creates a unary or binary filter that passes if the left operand is less than the right operand.', 'returns': 'Filter', 'type': 'Algorithm', 'hidden': False, 'name': 'Filter.lt'})
# Filter.lte
# Creates a unary or binary filter that passes unless the left operand is
# greater than the right operand.
#
# Args:
#   leftField: A selector for the left operand. Should not be
#       specified if leftValue is specified.
#   rightValue: The value of the right operand. Should not be
#       specified if rightField is specified.
#   rightField: A selector for the right operand. Should not be
#       specified if rightValue is specified.
#   leftValue: The value of the left operand. Should not be
#       specified if leftField is specified.
signatures.append({'args': [{'default': None, 'description': 'A selector for the left operand. Should not be specified if leftValue is specified.', 'name': 'leftField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the right operand. Should not be specified if rightField is specified.', 'name': 'rightValue', 'optional': True, 'type': 'Object'}, {'default': None, 'description': 'A selector for the right operand. Should not be specified if rightValue is specified.', 'name': 'rightField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the left operand. Should not be specified if leftField is specified.', 'name': 'leftValue', 'optional': True, 'type': 'Object'}], 'description': 'Creates a unary or binary filter that passes unless the left operand is greater than the right operand.', 'returns': 'Filter', 'type': 'Algorithm', 'hidden': False, 'name': 'Filter.lte'})
# Filter.maxDifference
# Creates a unary or binary filter that passes if the left and right
# operands, both numbers, are within a given maximum difference. If used as a
# join condition, this numeric difference is used as a join measure.
#
# Args:
#   difference: The maximum difference for which the filter
#       will return true.
#   leftField: A selector for the left operand. Should not be
#       specified if leftValue is specified.
#   rightValue: The value of the right operand. Should not be
#       specified if rightField is specified.
#   rightField: A selector for the right operand. Should not be
#       specified if rightValue is specified.
#   leftValue: The value of the left operand. Should not be
#       specified if leftField is specified.
signatures.append({'args': [{'description': 'The maximum difference for which the filter will return true.', 'name': 'difference', 'type': 'Float'}, {'default': None, 'description': 'A selector for the left operand. Should not be specified if leftValue is specified.', 'name': 'leftField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the right operand. Should not be specified if rightField is specified.', 'name': 'rightValue', 'optional': True, 'type': 'Object'}, {'default': None, 'description': 'A selector for the right operand. Should not be specified if rightValue is specified.', 'name': 'rightField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the left operand. Should not be specified if leftField is specified.', 'name': 'leftValue', 'optional': True, 'type': 'Object'}], 'description': 'Creates a unary or binary filter that passes if the left and right operands, both numbers, are within a given maximum difference. If used as a join condition, this numeric difference is used as a join measure.', 'returns': 'Filter', 'type': 'Algorithm', 'hidden': False, 'name': 'Filter.maxDifference'})
# Filter.neq
# Creates a unary or binary filter that passes unless the two operands are
# equals.
#
# Args:
#   leftField: A selector for the left operand. Should not be
#       specified if leftValue is specified.
#   rightValue: The value of the right operand. Should not be
#       specified if rightField is specified.
#   rightField: A selector for the right operand. Should not be
#       specified if rightValue is specified.
#   leftValue: The value of the left operand. Should not be
#       specified if leftField is specified.
signatures.append({'args': [{'default': None, 'description': 'A selector for the left operand. Should not be specified if leftValue is specified.', 'name': 'leftField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the right operand. Should not be specified if rightField is specified.', 'name': 'rightValue', 'optional': True, 'type': 'Object'}, {'default': None, 'description': 'A selector for the right operand. Should not be specified if rightValue is specified.', 'name': 'rightField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the left operand. Should not be specified if leftField is specified.', 'name': 'leftValue', 'optional': True, 'type': 'Object'}], 'description': 'Creates a unary or binary filter that passes unless the two operands are equals.', 'returns': 'Filter', 'type': 'Algorithm', 'hidden': False, 'name': 'Filter.neq'})
# Filter.never
# Simple filter NEVER.
signatures.append({'args': [], 'description': 'Simple filter NEVER.', 'returns': 'Filter', 'type': 'Algorithm', 'hidden': True, 'name': 'Filter.never'})
# Filter.not
# Returns a filter that passes if the provided filter fails.
#
# Args:
#   filter: The filter to negate.
signatures.append({'args': [{'description': 'The filter to negate.', 'name': 'filter', 'type': 'Filter'}], 'description': 'Returns a filter that passes if the provided filter fails.', 'returns': 'Filter', 'type': 'Algorithm', 'hidden': False, 'name': 'Filter.not'})
# Filter.notEquals
# Creates a unary or binary filter that passes unless the two operands are
# equals.
#
# Args:
#   leftField: A selector for the left operand. Should not be
#       specified if leftValue is specified.
#   rightValue: The value of the right operand. Should not be
#       specified if rightField is specified.
#   rightField: A selector for the right operand. Should not be
#       specified if rightValue is specified.
#   leftValue: The value of the left operand. Should not be
#       specified if leftField is specified.
signatures.append({'args': [{'default': None, 'description': 'A selector for the left operand. Should not be specified if leftValue is specified.', 'name': 'leftField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the right operand. Should not be specified if rightField is specified.', 'name': 'rightValue', 'optional': True, 'type': 'Object'}, {'default': None, 'description': 'A selector for the right operand. Should not be specified if rightValue is specified.', 'name': 'rightField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the left operand. Should not be specified if leftField is specified.', 'name': 'leftValue', 'optional': True, 'type': 'Object'}], 'description': 'Creates a unary or binary filter that passes unless the two operands are equals.', 'returns': 'Filter', 'type': 'Algorithm', 'hidden': False, 'name': 'Filter.notEquals'})
# Filter.notNull
# Creates a Filter.
#
# Args:
#   properties
signatures.append({'args': [{'name': 'properties', 'type': 'List'}], 'description': 'Creates a Filter.', 'returns': 'Filter', 'type': 'Algorithm', 'hidden': False, 'name': 'Filter.notNull'})
# Filter.or
# Returns a filter that passes if any of the component filters pass.
#
# Args:
#   filters: The filters to disjunct.
signatures.append({'args': [{'description': 'The filters to disjunct.', 'name': 'filters', 'type': 'List'}], 'description': 'Returns a filter that passes if any of the component filters pass.', 'returns': 'Filter', 'type': 'Algorithm', 'hidden': False, 'name': 'Filter.or'})
# Filter.rangeContains
# Returns a filter that passes if the value of the selected field is in the
# specified range (inclusive).
#
# Args:
#   field: A selector for the property being tested.
#   minValue: The lower bound of the range.
#   maxValue: The upper bound of the range.
signatures.append({'args': [{'description': 'A selector for the property being tested.', 'name': 'field', 'type': 'String'}, {'description': 'The lower bound of the range.', 'name': 'minValue', 'type': 'Object'}, {'description': 'The upper bound of the range.', 'name': 'maxValue', 'type': 'Object'}], 'description': 'Returns a filter that passes if the value of the selected field is in the specified range (inclusive).', 'returns': 'Filter', 'type': 'Algorithm', 'hidden': False, 'name': 'Filter.rangeContains'})
# Filter.stringContains
# Creates a unary or binary filter that passes if the left operand, a string,
# contains the right operand, also a string.
#
# Args:
#   leftField: A selector for the left operand. Should not be
#       specified if leftValue is specified.
#   rightValue: The value of the right operand. Should not be
#       specified if rightField is specified.
#   rightField: A selector for the right operand. Should not be
#       specified if rightValue is specified.
#   leftValue: The value of the left operand. Should not be
#       specified if leftField is specified.
signatures.append({'args': [{'default': None, 'description': 'A selector for the left operand. Should not be specified if leftValue is specified.', 'name': 'leftField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the right operand. Should not be specified if rightField is specified.', 'name': 'rightValue', 'optional': True, 'type': 'Object'}, {'default': None, 'description': 'A selector for the right operand. Should not be specified if rightValue is specified.', 'name': 'rightField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the left operand. Should not be specified if leftField is specified.', 'name': 'leftValue', 'optional': True, 'type': 'Object'}], 'description': 'Creates a unary or binary filter that passes if the left operand, a string, contains the right operand, also a string.', 'returns': 'Filter', 'type': 'Algorithm', 'hidden': False, 'name': 'Filter.stringContains'})
# Filter.stringEndsWith
# Creates a unary or binary filter that passes if the left operand, a string,
# ends with the right operand, also a string.
#
# Args:
#   leftField: A selector for the left operand. Should not be
#       specified if leftValue is specified.
#   rightValue: The value of the right operand. Should not be
#       specified if rightField is specified.
#   rightField: A selector for the right operand. Should not be
#       specified if rightValue is specified.
#   leftValue: The value of the left operand. Should not be
#       specified if leftField is specified.
signatures.append({'args': [{'default': None, 'description': 'A selector for the left operand. Should not be specified if leftValue is specified.', 'name': 'leftField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the right operand. Should not be specified if rightField is specified.', 'name': 'rightValue', 'optional': True, 'type': 'Object'}, {'default': None, 'description': 'A selector for the right operand. Should not be specified if rightValue is specified.', 'name': 'rightField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the left operand. Should not be specified if leftField is specified.', 'name': 'leftValue', 'optional': True, 'type': 'Object'}], 'description': 'Creates a unary or binary filter that passes if the left operand, a string, ends with the right operand, also a string.', 'returns': 'Filter', 'type': 'Algorithm', 'hidden': False, 'name': 'Filter.stringEndsWith'})
# Filter.stringStartsWith
# Creates a unary or binary filter that passes if the left operand, a string,
# starts with the right operand, also a string.
#
# Args:
#   leftField: A selector for the left operand. Should not be
#       specified if leftValue is specified.
#   rightValue: The value of the right operand. Should not be
#       specified if rightField is specified.
#   rightField: A selector for the right operand. Should not be
#       specified if rightValue is specified.
#   leftValue: The value of the left operand. Should not be
#       specified if leftField is specified.
signatures.append({'args': [{'default': None, 'description': 'A selector for the left operand. Should not be specified if leftValue is specified.', 'name': 'leftField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the right operand. Should not be specified if rightField is specified.', 'name': 'rightValue', 'optional': True, 'type': 'Object'}, {'default': None, 'description': 'A selector for the right operand. Should not be specified if rightValue is specified.', 'name': 'rightField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the left operand. Should not be specified if leftField is specified.', 'name': 'leftValue', 'optional': True, 'type': 'Object'}], 'description': 'Creates a unary or binary filter that passes if the left operand, a string, starts with the right operand, also a string.', 'returns': 'Filter', 'type': 'Algorithm', 'hidden': False, 'name': 'Filter.stringStartsWith'})
# Filter.withinDistance
# Creates a unary or binary filter that passes if the left geometry is within
# a specified distance of the right geometry. If used as a join condition,
# this distance is used as a join measure.
#
# Args:
#   distance: The maximum distance for which the filter will
#       return true.
#   leftField: A selector for the left operand. Should not be
#       specified if leftValue is specified.
#   rightValue: The value of the right operand. Should not be
#       specified if rightField is specified.
#   rightField: A selector for the right operand. Should not be
#       specified if rightValue is specified.
#   leftValue: The value of the left operand. Should not be
#       specified if leftField is specified.
#   maxError: The maximum reprojection error allowed during
#       filter application.
signatures.append({'args': [{'description': 'The maximum distance for which the filter will return true.', 'name': 'distance', 'type': 'Float'}, {'default': None, 'description': 'A selector for the left operand. Should not be specified if leftValue is specified.', 'name': 'leftField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the right operand. Should not be specified if rightField is specified.', 'name': 'rightValue', 'optional': True, 'type': 'Object'}, {'default': None, 'description': 'A selector for the right operand. Should not be specified if rightValue is specified.', 'name': 'rightField', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The value of the left operand. Should not be specified if leftField is specified.', 'name': 'leftValue', 'optional': True, 'type': 'Object'}, {'default': {'type': 'ErrorMargin', 'unit': 'meters', 'value': 0.1}, 'description': 'The maximum reprojection error allowed during filter application.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}], 'description': 'Creates a unary or binary filter that passes if the left geometry is within a specified distance of the right geometry. If used as a join condition, this distance is used as a join measure.', 'returns': 'Filter', 'type': 'Algorithm', 'hidden': False, 'name': 'Filter.withinDistance'})
# Geometry.area
# Returns the area of the geometry. Area of points and line strings is 0, and
# the area of multi geometries is the sum of the areas of their componenets
# (intersecting areas are counted multiple times).
#
# Args:
#   geometry: The geometry input.
#   maxError: The maximum amount of error tolerated when
#       performing any  necessary reprojection.
#   proj: If specified, the result will be in the units of the
#       coordinate system of this projection. Otherwise it  will be
#       in square meters.
signatures.append({'args': [{'description': 'The geometry input.', 'name': 'geometry', 'type': 'Geometry'}, {'default': None, 'description': 'The maximum amount of error tolerated when performing any  necessary reprojection.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}, {'default': None, 'description': 'If specified, the result will be in the units of the coordinate system of this projection. Otherwise it  will be in square meters.', 'name': 'proj', 'optional': True, 'type': 'Projection'}], 'description': 'Returns the area of the geometry. Area of points and line strings is 0, and the area of multi geometries is the sum of the areas of their componenets (intersecting areas are counted multiple times).', 'returns': 'Float', 'type': 'Algorithm', 'hidden': False, 'name': 'Geometry.area'})
# Geometry.bounds
# Returns the bounding rectangle of the geometry.
#
# Args:
#   geometry: Return the bounding box of this geometry.
#   maxError: The maximum amount of error tolerated when
#       performing any necessary reprojection.
#   proj: If specified, the result will be in this projection.
#       Otherwise it will be in WGS84.
signatures.append({'args': [{'description': 'Return the bounding box of this geometry.', 'name': 'geometry', 'type': 'Geometry'}, {'default': None, 'description': 'The maximum amount of error tolerated when performing any necessary reprojection.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}, {'default': None, 'description': 'If specified, the result will be in this projection. Otherwise it will be in WGS84.', 'name': 'proj', 'optional': True, 'type': 'Projection'}], 'description': 'Returns the bounding rectangle of the geometry.', 'returns': 'Geometry', 'type': 'Algorithm', 'hidden': False, 'name': 'Geometry.bounds'})
# Geometry.buffer
# Returns the input buffered by a given distance. If the distance is
# positive, the geometry is expanded, and if the distance is negative, the
# geometry is contracted.
#
# Args:
#   geometry: The geometry being buffered.
#   distance: The distance of the buffering, which may be
#       negative. If no projection is specified, the unit is
#       meters. Otherwise the unit is in the coordinate system of
#       the projection.
#   maxError: The maximum amount of error tolerated when
#       approximating the buffering circle and performing any
#       necessary reprojection. If unspecified, defaults to 1% of
#       the distance.
#   proj: If specified, the buffering will be performed in this
#       projection and the distance will be interpreted as units of
#       the coordinate system of this projection. Otherwise the
#       distance is interpereted as meters and the buffering is
#       performed in a spherical coordinate system.
signatures.append({'args': [{'description': 'The geometry being buffered.', 'name': 'geometry', 'type': 'Geometry'}, {'description': 'The distance of the buffering, which may be negative. If no projection is specified, the unit is meters. Otherwise the unit is in the coordinate system of the projection.', 'name': 'distance', 'type': 'Float'}, {'default': None, 'description': 'The maximum amount of error tolerated when approximating the buffering circle and performing any necessary reprojection. If unspecified, defaults to 1% of the distance.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}, {'default': None, 'description': 'If specified, the buffering will be performed in this projection and the distance will be interpreted as units of the coordinate system of this projection. Otherwise the distance is interpereted as meters and the buffering is performed in a spherical coordinate system.', 'name': 'proj', 'optional': True, 'type': 'Projection'}], 'description': 'Returns the input buffered by a given distance. If the distance is positive, the geometry is expanded, and if the distance is negative, the geometry is contracted.', 'returns': 'Geometry', 'type': 'Algorithm', 'hidden': False, 'name': 'Geometry.buffer'})
# Geometry.centroid
# Returns a point at the center of the highest-dimension components of the
# geometry. Lower-dimensional components are ignored, so the centroid of a
# geometry containing two polygons, three lines and a point is equivalent to
# the centroid of a geometry containing just the two polygons.
#
# Args:
#   geometry: Calculates the centroid of this geometry.
#   maxError: The maximum amount of error tolerated when
#       performing any necessary reprojection.
#   proj: If specified, the result will be in this projection.
#       Otherwise it will be in WGS84.
signatures.append({'args': [{'description': 'Calculates the centroid of this geometry.', 'name': 'geometry', 'type': 'Geometry'}, {'default': None, 'description': 'The maximum amount of error tolerated when performing any necessary reprojection.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}, {'default': None, 'description': 'If specified, the result will be in this projection. Otherwise it will be in WGS84.', 'name': 'proj', 'optional': True, 'type': 'Projection'}], 'description': 'Returns a point at the center of the highest-dimension components of the geometry. Lower-dimensional components are ignored, so the centroid of a geometry containing two polygons, three lines and a point is equivalent to the centroid of a geometry containing just the two polygons.', 'returns': 'Geometry', 'type': 'Algorithm', 'hidden': False, 'name': 'Geometry.centroid'})
# Geometry.containedIn
# Returns true iff one geometry is contained in the other.
#
# Args:
#   left: The geometry used as the left operand of the operation.
#   right: The geometry used as the right operand of the operation.
#   maxError: The maximum amount of error tolerated when
#       performing any necessary reprojection.
#   proj: The projection in which to perform the operation. If not
#       specified, the operation will be performed in a spherical
#       coordinate system, and linear distances will be in meters on
#       the sphere.
signatures.append({'args': [{'description': 'The geometry used as the left operand of the operation.', 'name': 'left', 'type': 'Geometry'}, {'description': 'The geometry used as the right operand of the operation.', 'name': 'right', 'type': 'Geometry'}, {'default': None, 'description': 'The maximum amount of error tolerated when performing any necessary reprojection.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}, {'default': None, 'description': 'The projection in which to perform the operation. If not specified, the operation will be performed in a spherical coordinate system, and linear distances will be in meters on the sphere.', 'name': 'proj', 'optional': True, 'type': 'Projection'}], 'description': 'Returns true iff one geometry is contained in the other.', 'returns': 'Boolean', 'type': 'Algorithm', 'hidden': False, 'name': 'Geometry.containedIn'})
# Geometry.contains
# Returns true iff one geometry contains the other.
#
# Args:
#   left: The geometry used as the left operand of the operation.
#   right: The geometry used as the right operand of the operation.
#   maxError: The maximum amount of error tolerated when
#       performing any necessary reprojection.
#   proj: The projection in which to perform the operation. If not
#       specified, the operation will be performed in a spherical
#       coordinate system, and linear distances will be in meters on
#       the sphere.
signatures.append({'args': [{'description': 'The geometry used as the left operand of the operation.', 'name': 'left', 'type': 'Geometry'}, {'description': 'The geometry used as the right operand of the operation.', 'name': 'right', 'type': 'Geometry'}, {'default': None, 'description': 'The maximum amount of error tolerated when performing any necessary reprojection.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}, {'default': None, 'description': 'The projection in which to perform the operation. If not specified, the operation will be performed in a spherical coordinate system, and linear distances will be in meters on the sphere.', 'name': 'proj', 'optional': True, 'type': 'Projection'}], 'description': 'Returns true iff one geometry contains the other.', 'returns': 'Boolean', 'type': 'Algorithm', 'hidden': False, 'name': 'Geometry.contains'})
# Geometry.convexHull
# Returns the convex hull of the given geometry. The convex hull of a single
# point is the point itself, the convex hull of collinear points is a line,
# and the convex hull of  everything else is a polygon. Note that a
# degenerate polygon with all vertices on the same line will result in a line
# segment.
#
# Args:
#   geometry: Calculates the convex hull of this geometry.
#   maxError: The maximum amount of error tolerated when
#       performing any necessary reprojection.
#   proj: The projection in which to perform the operation. If not
#       specified, the operation will be performed in a spherical
#       coordinate system, and linear distances will be in meters on
#       the sphere.
signatures.append({'args': [{'description': 'Calculates the convex hull of this geometry.', 'name': 'geometry', 'type': 'Geometry'}, {'default': None, 'description': 'The maximum amount of error tolerated when performing any necessary reprojection.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}, {'default': None, 'description': 'The projection in which to perform the operation. If not specified, the operation will be performed in a spherical coordinate system, and linear distances will be in meters on the sphere.', 'name': 'proj', 'optional': True, 'type': 'Projection'}], 'description': 'Returns the convex hull of the given geometry. The convex hull of a single point is the point itself, the convex hull of collinear points is a line, and the convex hull of  everything else is a polygon. Note that a degenerate polygon with all vertices on the same line will result in a line segment.', 'returns': 'Geometry', 'type': 'Algorithm', 'hidden': False, 'name': 'Geometry.convexHull'})
# Geometry.coordinates
# Returns a GeoJSON-style list of the geometry's coordinates.
#
# Args:
#   geometry
signatures.append({'args': [{'name': 'geometry', 'type': 'Geometry'}], 'description': "Returns a GeoJSON-style list of the geometry's coordinates.", 'returns': 'List', 'type': 'Algorithm', 'hidden': False, 'name': 'Geometry.coordinates'})
# Geometry.cutLines
# Converts LineStrings into a MultiLineString by cutting it in two at each
# distance along the length of the LineString.
#
# Args:
#   geometry: Cuts the lines of this geometry.
#   distances: Distances along each LineString to cut the line
#       into separate pieces, measured in units of the given
#       proj, or meters if proj is unspecified.
#   maxError: The maximum amount of error tolerated when
#       performing any necessary reprojection.
#   proj: Projection of the result and distance measurements, or
#       WGS84 if unspecified.
signatures.append({'args': [{'description': 'Cuts the lines of this geometry.', 'name': 'geometry', 'type': 'Geometry'}, {'description': 'Distances along each LineString to cut the line into separate pieces, measured in units of the given proj, or meters if proj is unspecified.', 'name': 'distances', 'type': 'List'}, {'default': None, 'description': 'The maximum amount of error tolerated when performing any necessary reprojection.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}, {'default': None, 'description': 'Projection of the result and distance measurements, or WGS84 if unspecified.', 'name': 'proj', 'optional': True, 'type': 'Projection'}], 'description': 'Converts LineStrings into a MultiLineString by cutting it in two at each distance along the length of the LineString.', 'returns': 'Geometry', 'type': 'Algorithm', 'hidden': False, 'name': 'Geometry.cutLines'})
# Geometry.difference
# Returns the result of subtracting the 'right' geometry from the 'left'
# geometry.
#
# Args:
#   left: The geometry used as the left operand of the operation.
#   right: The geometry used as the right operand of the operation.
#   maxError: The maximum amount of error tolerated when
#       performing any necessary reprojection.
#   proj: The projection in which to perform the operation. If not
#       specified, the operation will be performed in a spherical
#       coordinate system, and linear distances will be in meters on
#       the sphere.
signatures.append({'args': [{'description': 'The geometry used as the left operand of the operation.', 'name': 'left', 'type': 'Geometry'}, {'description': 'The geometry used as the right operand of the operation.', 'name': 'right', 'type': 'Geometry'}, {'default': None, 'description': 'The maximum amount of error tolerated when performing any necessary reprojection.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}, {'default': None, 'description': 'The projection in which to perform the operation. If not specified, the operation will be performed in a spherical coordinate system, and linear distances will be in meters on the sphere.', 'name': 'proj', 'optional': True, 'type': 'Projection'}], 'description': "Returns the result of subtracting the 'right' geometry from the 'left' geometry.", 'returns': 'Geometry', 'type': 'Algorithm', 'hidden': False, 'name': 'Geometry.difference'})
# Geometry.disjoint
# Returns true iff the geometries are disjoint.
#
# Args:
#   left: The geometry used as the left operand of the operation.
#   right: The geometry used as the right operand of the operation.
#   maxError: The maximum amount of error tolerated when
#       performing any necessary reprojection.
#   proj: The projection in which to perform the operation. If not
#       specified, the operation will be performed in a spherical
#       coordinate system, and linear distances will be in meters on
#       the sphere.
signatures.append({'args': [{'description': 'The geometry used as the left operand of the operation.', 'name': 'left', 'type': 'Geometry'}, {'description': 'The geometry used as the right operand of the operation.', 'name': 'right', 'type': 'Geometry'}, {'default': None, 'description': 'The maximum amount of error tolerated when performing any necessary reprojection.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}, {'default': None, 'description': 'The projection in which to perform the operation. If not specified, the operation will be performed in a spherical coordinate system, and linear distances will be in meters on the sphere.', 'name': 'proj', 'optional': True, 'type': 'Projection'}], 'description': 'Returns true iff the geometries are disjoint.', 'returns': 'Boolean', 'type': 'Algorithm', 'hidden': False, 'name': 'Geometry.disjoint'})
# Geometry.dissolve
# Returns the union of the geometry. This leaves single geometries untouched,
# and unions multi geometries.
#
# Args:
#   geometry: The geometry to union.
#   maxError: The maximum amount of error tolerated when
#       performing any  necessary reprojection.
#   proj: If specified, the union will be performed in this
#       projection. Otherwise it will be performed in a spherical
#       coordinate system.
signatures.append({'args': [{'description': 'The geometry to union.', 'name': 'geometry', 'type': 'Geometry'}, {'default': None, 'description': 'The maximum amount of error tolerated when performing any  necessary reprojection.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}, {'default': None, 'description': 'If specified, the union will be performed in this projection. Otherwise it will be performed in a spherical coordinate system.', 'name': 'proj', 'optional': True, 'type': 'Projection'}], 'description': 'Returns the union of the geometry. This leaves single geometries untouched, and unions multi geometries.', 'returns': 'Geometry', 'type': 'Algorithm', 'hidden': False, 'name': 'Geometry.dissolve'})
# Geometry.distance
# Returns the minimum distance between two geometries.
#
# Args:
#   left: The geometry used as the left operand of the operation.
#   right: The geometry used as the right operand of the operation.
#   maxError: The maximum amount of error tolerated when
#       performing any necessary reprojection.
#   proj: The projection in which to perform the operation. If not
#       specified, the operation will be performed in a spherical
#       coordinate system, and linear distances will be in meters on
#       the sphere.
signatures.append({'args': [{'description': 'The geometry used as the left operand of the operation.', 'name': 'left', 'type': 'Geometry'}, {'description': 'The geometry used as the right operand of the operation.', 'name': 'right', 'type': 'Geometry'}, {'default': None, 'description': 'The maximum amount of error tolerated when performing any necessary reprojection.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}, {'default': None, 'description': 'The projection in which to perform the operation. If not specified, the operation will be performed in a spherical coordinate system, and linear distances will be in meters on the sphere.', 'name': 'proj', 'optional': True, 'type': 'Projection'}], 'description': 'Returns the minimum distance between two geometries.', 'returns': 'Float', 'type': 'Algorithm', 'hidden': False, 'name': 'Geometry.distance'})
# Geometry.edgesAreGeodesics
# Returns true if the geometry edges, if any, are geodesics along a spherical
# model of the earth; if false, any edges are straight lines in the
# projection.
#
# Args:
#   geometry
signatures.append({'args': [{'name': 'geometry', 'type': 'Geometry'}], 'description': 'Returns true if the geometry edges, if any, are geodesics along a spherical model of the earth; if false, any edges are straight lines in the projection.', 'returns': 'Boolean', 'type': 'Algorithm', 'hidden': False, 'name': 'Geometry.edgesAreGeodesics'})
# Geometry.geodesic
# If false, edges are straight in the projection. If true, edges are curved
# to follow the shortest path on the surface of the Earth.
#
# Args:
#   geometry
signatures.append({'args': [{'name': 'geometry', 'type': 'Geometry'}], 'description': 'If false, edges are straight in the projection. If true, edges are curved to follow the shortest path on the surface of the Earth.', 'returns': 'Boolean', 'type': 'Algorithm', 'hidden': False, 'name': 'Geometry.geodesic'})
# Geometry.geometries
# Returns the list of geometries in a GeometryCollection, or a singleton list
# of the geometry for single geometries.
#
# Args:
#   geometry
signatures.append({'args': [{'name': 'geometry', 'type': 'Geometry'}], 'description': 'Returns the list of geometries in a GeometryCollection, or a singleton list of the geometry for single geometries.', 'returns': 'List', 'type': 'Algorithm', 'hidden': False, 'name': 'Geometry.geometries'})
# Geometry.intersection
# Returns the intersection of the two geometries.
#
# Args:
#   left: The geometry used as the left operand of the operation.
#   right: The geometry used as the right operand of the operation.
#   maxError: The maximum amount of error tolerated when
#       performing any necessary reprojection.
#   proj: The projection in which to perform the operation. If not
#       specified, the operation will be performed in a spherical
#       coordinate system, and linear distances will be in meters on
#       the sphere.
signatures.append({'args': [{'description': 'The geometry used as the left operand of the operation.', 'name': 'left', 'type': 'Geometry'}, {'description': 'The geometry used as the right operand of the operation.', 'name': 'right', 'type': 'Geometry'}, {'default': None, 'description': 'The maximum amount of error tolerated when performing any necessary reprojection.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}, {'default': None, 'description': 'The projection in which to perform the operation. If not specified, the operation will be performed in a spherical coordinate system, and linear distances will be in meters on the sphere.', 'name': 'proj', 'optional': True, 'type': 'Projection'}], 'description': 'Returns the intersection of the two geometries.', 'returns': 'Geometry', 'type': 'Algorithm', 'hidden': False, 'name': 'Geometry.intersection'})
# Geometry.intersects
# Returns true iff the geometries intersect.
#
# Args:
#   left: The geometry used as the left operand of the operation.
#   right: The geometry used as the right operand of the operation.
#   maxError: The maximum amount of error tolerated when
#       performing any necessary reprojection.
#   proj: The projection in which to perform the operation. If not
#       specified, the operation will be performed in a spherical
#       coordinate system, and linear distances will be in meters on
#       the sphere.
signatures.append({'args': [{'description': 'The geometry used as the left operand of the operation.', 'name': 'left', 'type': 'Geometry'}, {'description': 'The geometry used as the right operand of the operation.', 'name': 'right', 'type': 'Geometry'}, {'default': None, 'description': 'The maximum amount of error tolerated when performing any necessary reprojection.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}, {'default': None, 'description': 'The projection in which to perform the operation. If not specified, the operation will be performed in a spherical coordinate system, and linear distances will be in meters on the sphere.', 'name': 'proj', 'optional': True, 'type': 'Projection'}], 'description': 'Returns true iff the geometries intersect.', 'returns': 'Boolean', 'type': 'Algorithm', 'hidden': False, 'name': 'Geometry.intersects'})
# Geometry.isUnbounded
# Returns whether the geometry is unbounded.
#
# Args:
#   geometry
signatures.append({'args': [{'name': 'geometry', 'type': 'Geometry'}], 'description': 'Returns whether the geometry is unbounded.', 'returns': 'Boolean', 'type': 'Algorithm', 'hidden': False, 'name': 'Geometry.isUnbounded'})
# Geometry.length
# Returns the length of the linear parts of the geometry. Polygonal parts are
# ignored. The length of multi geometries is the sum of the lengths of their
# components.
#
# Args:
#   geometry: The input geometry.
#   maxError: The maximum amount of error tolerated when
#       performing any necessary reprojection.
#   proj: If specified, the result will be in the units of the
#       coordinate system of this projection. Otherwise it will be in
#       meters.
signatures.append({'args': [{'description': 'The input geometry.', 'name': 'geometry', 'type': 'Geometry'}, {'default': None, 'description': 'The maximum amount of error tolerated when performing any necessary reprojection.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}, {'default': None, 'description': 'If specified, the result will be in the units of the coordinate system of this projection. Otherwise it will be in meters.', 'name': 'proj', 'optional': True, 'type': 'Projection'}], 'description': 'Returns the length of the linear parts of the geometry. Polygonal parts are ignored. The length of multi geometries is the sum of the lengths of their components.', 'returns': 'Float', 'type': 'Algorithm', 'hidden': False, 'name': 'Geometry.length'})
# Geometry.perimeter
# Returns the length of the perimeter of the polygonal parts of the geometry.
# The perimeter of multi geometries is the sum of the perimeters of their
# components.
#
# Args:
#   geometry: The input geometry.
#   maxError: The maximum amount of error tolerated when
#       performing any necessary reprojection.
#   proj: If specified, the result will be in the units of the
#       coordinate system of this projection. Otherwise it will be in
#       meters.
signatures.append({'args': [{'description': 'The input geometry.', 'name': 'geometry', 'type': 'Geometry'}, {'default': None, 'description': 'The maximum amount of error tolerated when performing any necessary reprojection.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}, {'default': None, 'description': 'If specified, the result will be in the units of the coordinate system of this projection. Otherwise it will be in meters.', 'name': 'proj', 'optional': True, 'type': 'Projection'}], 'description': 'Returns the length of the perimeter of the polygonal parts of the geometry. The perimeter of multi geometries is the sum of the perimeters of their components.', 'returns': 'Float', 'type': 'Algorithm', 'hidden': False, 'name': 'Geometry.perimeter'})
# Geometry.projection
# Returns the projection of the geometry.
#
# Args:
#   geometry
signatures.append({'args': [{'name': 'geometry', 'type': 'Geometry'}], 'description': 'Returns the projection of the geometry.', 'returns': 'Projection', 'type': 'Algorithm', 'hidden': False, 'name': 'Geometry.projection'})
# Geometry.simplify
# Simplifies the geometry to within a given error margin. Note that this does
# not respect the error margin requested by the consumer of this algorithm,
# unless maxError is explicitly specified to be null. This overrides the
# default Earth Engine policy for propagating error margins, so regardless of
# the geometry accuracy requested from the output, the inputs will be
# requested with the error margin specified in the arguments to this
# algorithm. This results in consistent rendering at all zoom levels of a
# rendered vector map, but at lower zoom levels (i.e. zoomed out), the
# geometry won't be simplified, which may harm performance.
#
# Args:
#   geometry: The geometry to simplify.
#   maxError: The maximum amount of error by which the result may
#       differ from the input.
#   proj: If specified, the result will be in this projection.
#       Otherwise it will be in the same projection as the input. If
#       the error margin is in projected units, the margin will be
#       interpreted as units of this projection
signatures.append({'args': [{'description': 'The geometry to simplify.', 'name': 'geometry', 'type': 'Geometry'}, {'description': 'The maximum amount of error by which the result may differ from the input.', 'name': 'maxError', 'type': 'ErrorMargin'}, {'default': None, 'description': 'If specified, the result will be in this projection. Otherwise it will be in the same projection as the input. If the error margin is in projected units, the margin will be interpreted as units of this projection', 'name': 'proj', 'optional': True, 'type': 'Projection'}], 'description': "Simplifies the geometry to within a given error margin. Note that this does not respect the error margin requested by the consumer of this algorithm, unless maxError is explicitly specified to be null.\nThis overrides the default Earth Engine policy for propagating error margins, so regardless of the geometry accuracy requested from the output, the inputs will be requested with the error margin specified in the arguments to this algorithm. This results in consistent rendering at all zoom levels of a rendered vector map, but at lower zoom levels (i.e. zoomed out), the geometry won't be simplified, which may harm performance.", 'returns': 'Geometry', 'type': 'Algorithm', 'hidden': False, 'name': 'Geometry.simplify'})
# Geometry.snap
# Snaps the vertices of the  geometry to a regular cell grid with radius near
# but less than the given snap radius in meters. Snapping can reduce the
# number of vertices, close gaps in adjacent spatial features, and push
# degenerate elements to lower dimensional objects, e.g. a narrow polygon may
# collapse to a line. When applied to a GeometryCollection, overlap created
# between different elements is not removed.
#
# Args:
#   geometry: The geometry to snap.
#   snapRadius: The max distance to move vertices during
#       snapping. If in meters, 'proj' must not be specified,
#       otherwise if in units, 'proj' must specified.
#   proj: If unspecified the result will be in WGS84 with geodesic
#       edges and the snap radius must be in meters, otherwise the
#       snap radius must be in units and the result will be in this
#       projection with planar edges.
signatures.append({'args': [{'description': 'The geometry to snap.', 'name': 'geometry', 'type': 'Geometry'}, {'description': "The max distance to move vertices during snapping. If in meters, 'proj' must not be specified, otherwise if in units, 'proj' must specified.", 'name': 'snapRadius', 'type': 'ErrorMargin'}, {'default': None, 'description': 'If unspecified the result will be in WGS84 with geodesic edges and the snap radius must be in meters, otherwise the snap radius must be in units and the result will be in this projection with planar edges.', 'name': 'proj', 'optional': True, 'type': 'Projection'}], 'description': 'Snaps the vertices of the  geometry to a regular cell grid with radius near but less than the given snap radius in meters. Snapping can reduce the number of vertices, close gaps in adjacent spatial features, and push degenerate elements to lower dimensional objects, e.g. a narrow polygon may collapse to a line. When applied to a GeometryCollection, overlap created between different elements is not removed.', 'returns': 'Geometry', 'type': 'Algorithm', 'hidden': False, 'name': 'Geometry.snap'})
# Geometry.symmetricDifference
# Returns the symmetric difference between two geometries.
#
# Args:
#   left: The geometry used as the left operand of the operation.
#   right: The geometry used as the right operand of the operation.
#   maxError: The maximum amount of error tolerated when
#       performing any necessary reprojection.
#   proj: The projection in which to perform the operation. If not
#       specified, the operation will be performed in a spherical
#       coordinate system, and linear distances will be in meters on
#       the sphere.
signatures.append({'args': [{'description': 'The geometry used as the left operand of the operation.', 'name': 'left', 'type': 'Geometry'}, {'description': 'The geometry used as the right operand of the operation.', 'name': 'right', 'type': 'Geometry'}, {'default': None, 'description': 'The maximum amount of error tolerated when performing any necessary reprojection.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}, {'default': None, 'description': 'The projection in which to perform the operation. If not specified, the operation will be performed in a spherical coordinate system, and linear distances will be in meters on the sphere.', 'name': 'proj', 'optional': True, 'type': 'Projection'}], 'description': 'Returns the symmetric difference between two geometries.', 'returns': 'Geometry', 'type': 'Algorithm', 'hidden': False, 'name': 'Geometry.symmetricDifference'})
# Geometry.transform
# Transforms the geometry to a specific projection.
#
# Args:
#   geometry: The geometry to reproject.
#   proj: The target projection. Defaults to WGS84. If this has a
#       geographic CRS, the edges of the geometry will be interpreted
#       as geodesics. Otherwise they will be interpreted as straight
#       lines in the projection.
#   maxError: The maximum projection error.
signatures.append({'args': [{'description': 'The geometry to reproject.', 'name': 'geometry', 'type': 'Geometry'}, {'default': {'crs': 'EPSG:4326', 'transform': [1.0, 0.0, 0.0, 0.0, 1.0, 0.0], 'type': 'Projection'}, 'description': 'The target projection. Defaults to WGS84. If this has a geographic CRS, the edges of the geometry will be interpreted as geodesics. Otherwise they will be interpreted as straight lines in the projection.', 'name': 'proj', 'optional': True, 'type': 'Projection'}, {'default': None, 'description': 'The maximum projection error.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}], 'description': 'Transforms the geometry to a specific projection.', 'returns': 'Geometry', 'type': 'Algorithm', 'hidden': False, 'name': 'Geometry.transform'})
# Geometry.type
# Returns the GeoJSON type of the geometry.
#
# Args:
#   geometry
signatures.append({'args': [{'name': 'geometry', 'type': 'Geometry'}], 'description': 'Returns the GeoJSON type of the geometry.', 'returns': 'String', 'type': 'Algorithm', 'hidden': False, 'name': 'Geometry.type'})
# Geometry.union
# Returns the union of the two geometries.
#
# Args:
#   left: The geometry used as the left operand of the operation.
#   right: The geometry used as the right operand of the operation.
#   maxError: The maximum amount of error tolerated when
#       performing any necessary reprojection.
#   proj: The projection in which to perform the operation. If not
#       specified, the operation will be performed in a spherical
#       coordinate system, and linear distances will be in meters on
#       the sphere.
signatures.append({'args': [{'description': 'The geometry used as the left operand of the operation.', 'name': 'left', 'type': 'Geometry'}, {'description': 'The geometry used as the right operand of the operation.', 'name': 'right', 'type': 'Geometry'}, {'default': None, 'description': 'The maximum amount of error tolerated when performing any necessary reprojection.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}, {'default': None, 'description': 'The projection in which to perform the operation. If not specified, the operation will be performed in a spherical coordinate system, and linear distances will be in meters on the sphere.', 'name': 'proj', 'optional': True, 'type': 'Projection'}], 'description': 'Returns the union of the two geometries.', 'returns': 'Geometry', 'type': 'Algorithm', 'hidden': False, 'name': 'Geometry.union'})
# Geometry.withinDistance
# Returns true iff the geometries are within a specified distance.
#
# Args:
#   left: The geometry used as the left operand of the operation.
#   right: The geometry used as the right operand of the operation.
#   distance: The distance threshold. If a projection is
#       specified, the distance is in units of that projected
#       coordinate system, otherwise it is in meters.
#   maxError: The maximum amount of error tolerated when
#       performing any necessary reprojection.
#   proj: The projection in which to perform the operation. If not
#       specified, the operation will be performed in a spherical
#       coordinate system, and linear distances will be in meters on
#       the sphere.
signatures.append({'args': [{'description': 'The geometry used as the left operand of the operation.', 'name': 'left', 'type': 'Geometry'}, {'description': 'The geometry used as the right operand of the operation.', 'name': 'right', 'type': 'Geometry'}, {'description': 'The distance threshold. If a projection is specified, the distance is in units of that projected coordinate system, otherwise it is in meters.', 'name': 'distance', 'type': 'Float'}, {'default': None, 'description': 'The maximum amount of error tolerated when performing any necessary reprojection.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}, {'default': None, 'description': 'The projection in which to perform the operation. If not specified, the operation will be performed in a spherical coordinate system, and linear distances will be in meters on the sphere.', 'name': 'proj', 'optional': True, 'type': 'Projection'}], 'description': 'Returns true iff the geometries are within a specified distance.', 'returns': 'Boolean', 'type': 'Algorithm', 'hidden': False, 'name': 'Geometry.withinDistance'})
# GeometryConstructors.LineString
# Constructs a LineString from the given coordinates.
#
# Args:
#   coordinates: The list of Points or pairs of Numbers in x,y
#       order.
#   crs: The coordinate reference system of the coordinates. The
#       default is the projection of the inputs, where Numbers are
#       assumed to be EPSG:4326.
#   geodesic: If false, edges are straight in the projection. If
#       true, edges are curved to follow the shortest path on the
#       surface of the Earth. The default is the geodesic state
#       of the inputs, or true if the inputs are numbers.
signatures.append({'args': [{'description': 'The list of Points or pairs of Numbers in x,y order.', 'name': 'coordinates', 'type': 'List'}, {'default': None, 'description': 'The coordinate reference system of the coordinates. The  default is the projection of the inputs, where Numbers are assumed to be EPSG:4326.', 'name': 'crs', 'optional': True, 'type': 'Projection'}, {'default': None, 'description': 'If false, edges are straight in the projection. If true, edges are curved to follow the shortest path on the surface of the Earth. The default is the geodesic state of the inputs, or true if the inputs are numbers.', 'name': 'geodesic', 'optional': True, 'type': 'Boolean'}], 'description': 'Constructs a LineString from the given coordinates.', 'returns': 'Geometry', 'type': 'Algorithm', 'hidden': False, 'name': 'GeometryConstructors.LineString'})
# GeometryConstructors.LinearRing
# Constructs a LinearRing from the given coordinates, automatically adding
# the first point at the end if the ring is not explicitly closed.
#
# Args:
#   coordinates: The list of Points or pairs of Numbers in x,y
#       order.
#   crs: The coordinate reference system of the coordinates. The
#       default is the projection of the inputs, where Numbers are
#       assumed to be EPSG:4326.
#   geodesic: If false, edges are straight in the projection. If
#       true, edges are curved to follow the shortest path on the
#       surface of the Earth. The default is the geodesic state
#       of the inputs, or true if the inputs are numbers.
signatures.append({'args': [{'description': 'The list of Points or pairs of Numbers in x,y order.', 'name': 'coordinates', 'type': 'List'}, {'default': None, 'description': 'The coordinate reference system of the coordinates. The  default is the projection of the inputs, where Numbers are assumed to be EPSG:4326.', 'name': 'crs', 'optional': True, 'type': 'Projection'}, {'default': None, 'description': 'If false, edges are straight in the projection. If true, edges are curved to follow the shortest path on the surface of the Earth. The default is the geodesic state of the inputs, or true if the inputs are numbers.', 'name': 'geodesic', 'optional': True, 'type': 'Boolean'}], 'description': 'Constructs a LinearRing from the given coordinates, automatically adding the first point at the end if the ring is not explicitly closed.', 'returns': 'Geometry', 'type': 'Algorithm', 'hidden': False, 'name': 'GeometryConstructors.LinearRing'})
# GeometryConstructors.MultiGeometry
# Constructs a MultiGeometry from the given list of geometry elements.
#
# Args:
#   geometries: The list of geometries for the MultiGeometry.
#   crs: The coordinate reference system of the coordinates. The
#       default is the projection of the inputs, where Numbers are
#       assumed to be EPSG:4326.
#   geodesic: If false, edges are straight in the projection. If
#       true, edges are curved to follow the shortest path on the
#       surface of the Earth. The default is the geodesic state
#       of the inputs, or true if the inputs are numbers.
#   maxError: Max error when input geometry must be reprojected
#       to an explicitly requested result projection or geodesic
#       state.
signatures.append({'args': [{'description': 'The list of geometries for the MultiGeometry.', 'name': 'geometries', 'type': 'List'}, {'default': None, 'description': 'The coordinate reference system of the coordinates. The  default is the projection of the inputs, where Numbers are assumed to be EPSG:4326.', 'name': 'crs', 'optional': True, 'type': 'Projection'}, {'default': None, 'description': 'If false, edges are straight in the projection. If true, edges are curved to follow the shortest path on the surface of the Earth. The default is the geodesic state of the inputs, or true if the inputs are numbers.', 'name': 'geodesic', 'optional': True, 'type': 'Boolean'}, {'default': None, 'description': 'Max error when input geometry must be reprojected to an explicitly requested result projection or geodesic state.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}], 'description': 'Constructs a MultiGeometry from the given list of geometry elements.', 'returns': 'Geometry', 'type': 'Algorithm', 'hidden': False, 'name': 'GeometryConstructors.MultiGeometry'})
# GeometryConstructors.MultiLineString
# Constructs a MultiLineString from the given coordinates.
#
# Args:
#   coordinates: The list of LineStrings, or to wrap a single
#       LineString, the list of Points or pairs of Numbers in
#       x,y order.
#   crs: The coordinate reference system of the coordinates. The
#       default is the projection of the inputs, where Numbers are
#       assumed to be EPSG:4326.
#   geodesic: If false, edges are straight in the projection. If
#       true, edges are curved to follow the shortest path on the
#       surface of the Earth. The default is the geodesic state
#       of the inputs, or true if the inputs are numbers.
#   maxError: Max error when input geometry must be reprojected
#       to an explicitly requested result projection or geodesic
#       state.
signatures.append({'args': [{'description': 'The list of LineStrings, or to wrap a single LineString, the list of Points or pairs of Numbers in x,y order.', 'name': 'coordinates', 'type': 'List'}, {'default': None, 'description': 'The coordinate reference system of the coordinates. The  default is the projection of the inputs, where Numbers are assumed to be EPSG:4326.', 'name': 'crs', 'optional': True, 'type': 'Projection'}, {'default': None, 'description': 'If false, edges are straight in the projection. If true, edges are curved to follow the shortest path on the surface of the Earth. The default is the geodesic state of the inputs, or true if the inputs are numbers.', 'name': 'geodesic', 'optional': True, 'type': 'Boolean'}, {'default': None, 'description': 'Max error when input geometry must be reprojected to an explicitly requested result projection or geodesic state.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}], 'description': 'Constructs a MultiLineString from the given coordinates.', 'returns': 'Geometry', 'type': 'Algorithm', 'hidden': False, 'name': 'GeometryConstructors.MultiLineString'})
# GeometryConstructors.MultiPoint
# Constructs a MultiPoint from the given coordinates.
#
# Args:
#   coordinates: The list of Points or pairs of Numbers in x,y
#       order.
#   crs: The coordinate reference system of the coordinates. The
#       default is the projection of the inputs, where Numbers are
#       assumed to be EPSG:4326.
signatures.append({'args': [{'description': 'The list of Points or pairs of Numbers in x,y order.', 'name': 'coordinates', 'type': 'List'}, {'default': None, 'description': 'The coordinate reference system of the coordinates. The  default is the projection of the inputs, where Numbers are assumed to be EPSG:4326.', 'name': 'crs', 'optional': True, 'type': 'Projection'}], 'description': 'Constructs a MultiPoint from the given coordinates.', 'returns': 'Geometry', 'type': 'Algorithm', 'hidden': False, 'name': 'GeometryConstructors.MultiPoint'})
# GeometryConstructors.MultiPolygon
# Constructs a MultiPolygon from the given coordinates.
#
# Args:
#   coordinates: A list of Polygons, or for one simple
#       polygon, a list of Points or pairs of Numbers in x,y
#       order.
#   crs: The coordinate reference system of the coordinates. The
#       default is the projection of the inputs, where Numbers are
#       assumed to be EPSG:4326.
#   geodesic: If false, edges are straight in the projection. If
#       true, edges are curved to follow the shortest path on the
#       surface of the Earth. The default is the geodesic state
#       of the inputs, or true if the inputs are numbers.
#   maxError: Max error when input geometry must be reprojected
#       to an explicitly requested result projection or geodesic
#       state.
#   evenOdd: If true, polygon interiors will be determined by the
#       even/odd rule, where a point is inside if it crosses an
#       odd number of edges to reach a point at infinity.
#       Otherwise polygons use the left-inside rule, where
#       interiors are on the left side of the shell's edges when
#       walking the vertices in the given order.
signatures.append({'args': [{'description': 'A list of Polygons, or for one simple polygon, a list of Points or pairs of Numbers in x,y order.', 'name': 'coordinates', 'type': 'List'}, {'default': None, 'description': 'The coordinate reference system of the coordinates. The  default is the projection of the inputs, where Numbers are assumed to be EPSG:4326.', 'name': 'crs', 'optional': True, 'type': 'Projection'}, {'default': None, 'description': 'If false, edges are straight in the projection. If true, edges are curved to follow the shortest path on the surface of the Earth. The default is the geodesic state of the inputs, or true if the inputs are numbers.', 'name': 'geodesic', 'optional': True, 'type': 'Boolean'}, {'default': None, 'description': 'Max error when input geometry must be reprojected to an explicitly requested result projection or geodesic state.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}, {'default': True, 'description': "If true, polygon interiors will be determined by the even/odd rule, where a point is inside if it crosses an odd number of edges to reach a point at infinity. Otherwise polygons use the left-inside rule, where interiors are on the left side of the shell's edges when walking the vertices in the given order.", 'name': 'evenOdd', 'optional': True, 'type': 'Boolean'}], 'description': 'Constructs a MultiPolygon from the given coordinates.', 'returns': 'Geometry', 'type': 'Algorithm', 'hidden': False, 'name': 'GeometryConstructors.MultiPolygon'})
# GeometryConstructors.Point
# Constructs a new Point from the given x,y coordinates.
#
# Args:
#   coordinates: The coordinates of this Point in x,y order.
#   crs: The coordinate reference system of the coordinates. The
#       default is the projection of the inputs, where Numbers are
#       assumed to be EPSG:4326.
signatures.append({'args': [{'description': 'The coordinates of this Point in x,y order.', 'name': 'coordinates', 'type': 'List'}, {'default': None, 'description': 'The coordinate reference system of the coordinates. The  default is the projection of the inputs, where Numbers are assumed to be EPSG:4326.', 'name': 'crs', 'optional': True, 'type': 'Projection'}], 'description': 'Constructs a new Point from the given x,y coordinates.', 'returns': 'Geometry', 'type': 'Algorithm', 'hidden': False, 'name': 'GeometryConstructors.Point'})
# GeometryConstructors.Polygon
# Constructs a Polygon from the given coordinates.
#
# Args:
#   coordinates: A list of LinearRings where the first is the
#       shell and the rest are holes, or for a simple polygon,
#       a list of Points or pairs of Numbers in x,y order.
#   crs: The coordinate reference system of the coordinates. The
#       default is the projection of the inputs, where Numbers are
#       assumed to be EPSG:4326.
#   geodesic: If false, edges are straight in the projection. If
#       true, edges are curved to follow the shortest path on the
#       surface of the Earth. The default is the geodesic state
#       of the inputs, or true if the inputs are numbers.
#   maxError: Max error when input geometry must be reprojected
#       to an explicitly requested result projection or geodesic
#       state.
#   evenOdd: If true, polygon interiors will be determined by the
#       even/odd rule, where a point is inside if it crosses an
#       odd number of edges to reach a point at infinity.
#       Otherwise polygons use the left-inside rule, where
#       interiors are on the left side of the shell's edges when
#       walking the vertices in the given order.
signatures.append({'args': [{'description': 'A list of LinearRings where the first is the shell and the rest are holes, or for a simple polygon, a list of Points or pairs of Numbers in x,y order.', 'name': 'coordinates', 'type': 'List'}, {'default': None, 'description': 'The coordinate reference system of the coordinates. The  default is the projection of the inputs, where Numbers are assumed to be EPSG:4326.', 'name': 'crs', 'optional': True, 'type': 'Projection'}, {'default': None, 'description': 'If false, edges are straight in the projection. If true, edges are curved to follow the shortest path on the surface of the Earth. The default is the geodesic state of the inputs, or true if the inputs are numbers.', 'name': 'geodesic', 'optional': True, 'type': 'Boolean'}, {'default': None, 'description': 'Max error when input geometry must be reprojected to an explicitly requested result projection or geodesic state.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}, {'default': True, 'description': "If true, polygon interiors will be determined by the even/odd rule, where a point is inside if it crosses an odd number of edges to reach a point at infinity. Otherwise polygons use the left-inside rule, where interiors are on the left side of the shell's edges when walking the vertices in the given order.", 'name': 'evenOdd', 'optional': True, 'type': 'Boolean'}], 'description': 'Constructs a Polygon from the given coordinates.', 'returns': 'Geometry', 'type': 'Algorithm', 'hidden': False, 'name': 'GeometryConstructors.Polygon'})
# GeometryConstructors.Rectangle
# Constructs a rectangular polygon from the given corner points.
#
# Args:
#   coordinates: The low and then high corners of the
#       Rectangle, as a list of Points or pairs of Numbers in
#       x,y order.
#   crs: The coordinate reference system of the coordinates. The
#       default is the projection of the inputs, where Numbers are
#       assumed to be EPSG:4326.
#   geodesic: If false, edges are straight in the projection. If
#       true, edges are curved to follow the shortest path on the
#       surface of the Earth. The default is the geodesic state
#       of the inputs, or true if the inputs are numbers.
#   evenOdd: If true, polygon interiors will be determined by the
#       even/odd rule, where a point is inside if it crosses an
#       odd number of edges to reach a point at infinity.
#       Otherwise polygons use the left-inside rule, where
#       interiors are on the left side of the shell's edges when
#       walking the vertices in the given order.
signatures.append({'args': [{'description': 'The low and then high corners of the Rectangle, as a list of Points or pairs of Numbers in x,y order.', 'name': 'coordinates', 'type': 'List'}, {'default': None, 'description': 'The coordinate reference system of the coordinates. The  default is the projection of the inputs, where Numbers are assumed to be EPSG:4326.', 'name': 'crs', 'optional': True, 'type': 'Projection'}, {'default': None, 'description': 'If false, edges are straight in the projection. If true, edges are curved to follow the shortest path on the surface of the Earth. The default is the geodesic state of the inputs, or true if the inputs are numbers.', 'name': 'geodesic', 'optional': True, 'type': 'Boolean'}, {'default': True, 'description': "If true, polygon interiors will be determined by the even/odd rule, where a point is inside if it crosses an odd number of edges to reach a point at infinity. Otherwise polygons use the left-inside rule, where interiors are on the left side of the shell's edges when walking the vertices in the given order.", 'name': 'evenOdd', 'optional': True, 'type': 'Boolean'}], 'description': 'Constructs a rectangular polygon from the given corner points.', 'returns': 'Geometry', 'type': 'Algorithm', 'hidden': False, 'name': 'GeometryConstructors.Rectangle'})
# HillShadow
# Creates a shadow band, with output 1 where pixels are illumunated and 0
# where they are shadowed. Takes as input an elevation band, azimuth and
# zenith of the light source in degrees, a neighborhood size, and whether or
# not to apply hysteresis when a shadow appears. Currently, this algorithm
# only works for Mercator projections, in which light rays are parallel.
#
# Args:
#   image: The image to which to apply the shadow algorithm, in
#       whicheach pixel should represent an elevation in meters.
#   azimuth: Azimuth in degrees.
#   zenith: Zenith in degrees.
#   neighborhoodSize: Neighborhood size.
#   hysteresis: Use hysteresis. Less physically accurate, but
#       may generate better images.
signatures.append({'args': [{'description': 'The image to which to apply the shadow algorithm, in whicheach pixel should represent an elevation in meters.', 'name': 'image', 'type': 'Image'}, {'description': 'Azimuth in degrees.', 'name': 'azimuth', 'type': 'Float'}, {'description': 'Zenith in degrees.', 'name': 'zenith', 'type': 'Float'}, {'default': 0, 'description': 'Neighborhood size.', 'name': 'neighborhoodSize', 'optional': True, 'type': 'Integer'}, {'default': False, 'description': 'Use hysteresis. Less physically accurate, but may generate better images.', 'name': 'hysteresis', 'optional': True, 'type': 'Boolean'}], 'description': 'Creates a shadow band, with output 1 where pixels are illumunated and 0 where they are shadowed. Takes as input an elevation band, azimuth and zenith of the light source in degrees, a neighborhood size, and whether or not to apply hysteresis when a shadow appears. Currently, this algorithm only works for Mercator projections, in which light rays are parallel.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'HillShadow'})
# HoughTransform
# Applies the Hough transform to an image. For every input band, outputs a
# band where lines are detected by thresholding the Hough transform with a
# value of lineThreshold. The output band is named [input]_lines, where
# [input] is the name of the original band. The defaults provided for the
# parameters are intended as a starting point for use with UINT8 images.
#
# Args:
#   image: The image to which to apply the transform.
#   gridSize: Grid size.
#   inputThreshold: Value threshold for input image. Pixels
#       equal to or above this value are considered active.
#   lineThreshold: Threshold for line detection. Values
#       equal to or above this threshold on the Hough
#       transform are considered to be detected lines.
#   smooth: Whether to smooth the Hough transform before line
#       detection.
signatures.append({'args': [{'description': 'The image to which to apply the transform.', 'name': 'image', 'type': 'Image'}, {'default': 256, 'description': 'Grid size.', 'name': 'gridSize', 'optional': True, 'type': 'Integer'}, {'default': 64.0, 'description': 'Value threshold for input image. Pixels equal to or above this value are considered active.', 'name': 'inputThreshold', 'optional': True, 'type': 'Float'}, {'default': 72.0, 'description': 'Threshold for line detection. Values equal to or above this threshold on the Hough transform are considered to be detected lines.', 'name': 'lineThreshold', 'optional': True, 'type': 'Float'}, {'default': True, 'description': 'Whether to smooth the Hough transform before line detection.', 'name': 'smooth', 'optional': True, 'type': 'Boolean'}], 'description': 'Applies the Hough transform to an image. For every input band, outputs a band where lines are detected by thresholding the Hough transform with a value of lineThreshold. The output band is named [input]_lines, where [input] is the name of the original band. The defaults provided for the parameters are intended as a starting point for use with UINT8 images. ', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'HoughTransform'})
# If
# Selects one of its inputs based on a condition, similar to an if-then-else
# construct.
#
# Args:
#   condition: The condition that determines which result is
#       returned. If this is not a boolean, it is interpreted as
#       a boolean by the following rules:   - Numbers that are
#       equal to 0 or a NaN are false.   - Empty strings, lists
#       and dictionaries are false.   - Null is false.   -
#       Everything else is true.
#   trueCase: The result to return if the condition is true.
#   falseCase: The result to return if the condition is false.
signatures.append({'args': [{'default': None, 'description': 'The condition that determines which result is returned. If this is not a boolean, it is interpreted as a boolean by the following rules:\n  - Numbers that are equal to 0 or a NaN are false.\n  - Empty strings, lists and dictionaries are false.\n  - Null is false.\n  - Everything else is true.', 'name': 'condition', 'optional': True, 'type': 'Object'}, {'default': None, 'description': 'The result to return if the condition is true.', 'name': 'trueCase', 'optional': True, 'type': 'Object'}, {'default': None, 'description': 'The result to return if the condition is false.', 'name': 'falseCase', 'optional': True, 'type': 'Object'}], 'description': 'Selects one of its inputs based on a condition, similar to an if-then-else construct.', 'returns': 'Object', 'type': 'Algorithm', 'hidden': False, 'name': 'If'})
# Image.Segmentation.GMeans
# Performs G-Means clustering on the input image. Iteratively applies k-means
# followed by a normality test to automatically determine the number of
# clusters to use. The output contains a 'clusters' band containing the
# integer ID of the cluster that each pixel belongs to. The algorithm can
# work either on a fixed grid of non-overlapping cells (gridSize, which can
# be smaller than a tile) or on tiles with overlap (neighborhoodSize). The
# default is to use tiles with no overlap. Clusters in one cell or tile are
# unrelated to clusters in another. Any cluster that spans a cell or tile
# boundary may receive two different labels in the two halves. Any input
# pixels with partial masks are fully masked in the output. This algorithm is
# only expected to perform well for images with a narrow dynamic range (i.e.
# bytes or shorts). See: G. Hamerly and C. Elkan. 'Learning the k in
# k-means'. NIPS, 2003.
#
# Args:
#   image: The input image for clustering.
#   numIterations: Number of iterations. Default 10.
#   pValue: Significance level for normality test.
#   neighborhoodSize: Neighborhood size.  The amount to
#       extend each tile (overlap) when computing the
#       clusters. This option is mutually exclusive with
#       gridSize.
#   gridSize: Grid cell-size.  If greater than 0, kMeans will be
#       run independently on cells of this size. This has the
#       effect of limiting the size of any cluster to be gridSize
#       or smaller.  This option is mutually exclusive with
#       neighborhoodSize.
#   uniqueLabels: If true, clusters are assigned unique IDs.
#       Otherwise, they repeat per tile or grid cell.
signatures.append({'args': [{'description': 'The input image for clustering.', 'name': 'image', 'type': 'Image'}, {'default': 10, 'description': 'Number of iterations. Default 10.', 'name': 'numIterations', 'optional': True, 'type': 'Integer'}, {'default': 50.0, 'description': 'Significance level for normality test.', 'name': 'pValue', 'optional': True, 'type': 'Float'}, {'default': 0, 'description': 'Neighborhood size.  The amount to extend each tile (overlap) when computing the clusters. This option is mutually exclusive with gridSize.', 'name': 'neighborhoodSize', 'optional': True, 'type': 'Integer'}, {'default': None, 'description': 'Grid cell-size.  If greater than 0, kMeans will be run independently on cells of this size. This has the effect of limiting the size of any cluster to be gridSize or smaller.  This option is mutually exclusive with neighborhoodSize.', 'name': 'gridSize', 'optional': True, 'type': 'Integer'}, {'default': True, 'description': 'If true, clusters are assigned unique IDs. Otherwise, they repeat per tile or grid cell.', 'name': 'uniqueLabels', 'optional': True, 'type': 'Boolean'}], 'description': "Performs G-Means clustering on the input image. Iteratively applies k-means followed by a normality test to automatically determine the number of clusters to use. The output contains a 'clusters' band containing the integer ID of the cluster that each pixel belongs to. The algorithm can work either on a fixed grid of non-overlapping cells (gridSize, which can be smaller than a tile) or on tiles with overlap (neighborhoodSize). The default is to use tiles with no overlap. Clusters in one cell or tile are unrelated to clusters in another. Any cluster that spans a cell or tile boundary may receive two different labels in the two halves. Any input pixels with partial masks are fully masked in the output. This algorithm is only expected to perform well for images with a narrow dynamic range (i.e. bytes or shorts).\nSee: G. Hamerly and C. Elkan. 'Learning the k in k-means'. NIPS, 2003.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.Segmentation.GMeans'})
# Image.Segmentation.KMeans
# Performs K-Means clustering on the input image. Outputs a 1-band image
# containing the ID of the cluster that each pixel belongs to.  The algorithm
# can work either on a fixed grid of non-overlapping cells (gridSize, which
# can be smaller than a tile) or on tiles with overlap (neighborhoodSize).
# The default is to use tiles with no overlap.  Clusters in one cell or tile
# are unrelated to clusters in another.  Any cluster that spans a cell or
# tile boundary may receive two different labels in the two halves.  Any
# input pixels with partial masks are fully masked in the output.
#
# Args:
#   image: The input image for clustering.
#   numClusters: Number of clusters.
#   numIterations: Number of iterations.
#   neighborhoodSize: Neighborhood size.  The amount to
#       extend each tile (overlap) when computing the
#       clusters. This option is mutually exclusive with
#       gridSize.
#   gridSize: Grid cell-size.  If greater than 0, kMeans will be
#       run independently on cells of this size. This has the
#       effect of limiting the size of any cluster to be gridSize
#       or smaller.  This option is mutually exclusive with
#       neighborhoodSize.
#   forceConvergence: If true, an error is thrown if
#       convergence is not achieved before numIterations.
#   uniqueLabels: If true, clusters are assigned unique IDs.
#       Otherwise, they repeat per tile or grid cell.
signatures.append({'args': [{'description': 'The input image for clustering.', 'name': 'image', 'type': 'Image'}, {'default': 8, 'description': 'Number of clusters.', 'name': 'numClusters', 'optional': True, 'type': 'Integer'}, {'default': 20, 'description': 'Number of iterations.', 'name': 'numIterations', 'optional': True, 'type': 'Integer'}, {'default': 0, 'description': 'Neighborhood size.  The amount to extend each tile (overlap) when computing the clusters. This option is mutually exclusive with gridSize.', 'name': 'neighborhoodSize', 'optional': True, 'type': 'Integer'}, {'default': None, 'description': 'Grid cell-size.  If greater than 0, kMeans will be run independently on cells of this size. This has the effect of limiting the size of any cluster to be gridSize or smaller.  This option is mutually exclusive with neighborhoodSize.', 'name': 'gridSize', 'optional': True, 'type': 'Integer'}, {'default': False, 'description': 'If true, an error is thrown if convergence is not achieved before numIterations.', 'name': 'forceConvergence', 'optional': True, 'type': 'Boolean'}, {'default': True, 'description': 'If true, clusters are assigned unique IDs. Otherwise, they repeat per tile or grid cell.', 'name': 'uniqueLabels', 'optional': True, 'type': 'Boolean'}], 'description': 'Performs K-Means clustering on the input image. Outputs a 1-band image  containing the ID of the cluster that each pixel belongs to.  The algorithm can work either on a fixed grid of non-overlapping cells (gridSize, which can be smaller than a tile) or on tiles with overlap (neighborhoodSize). The default is to use tiles with no overlap.  Clusters in one cell or tile are unrelated to clusters in another.  Any cluster that spans a cell or tile boundary may receive two different labels in the two halves.  Any input pixels with partial masks are fully masked in the output.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.Segmentation.KMeans'})
# Image.Segmentation.SNIC
# Superpixel clustering based on SNIC (Simple Non-Iterative Clustering).
# Outputs a band of cluster IDs and the per-cluster averages for each of the
# input bands. If the 'seeds' image isn't provided as input, the output will
# include a 'seeds' band containing the generated seed locations. See:
# Achanta, Radhakrishna and Susstrunk, Sabine, 'Superpixels and Polygons
# using Simple Non-Iterative Clustering', CVPR, 2017.
#
# Args:
#   image: The input image for clustering.
#   size: The superpixel seed location spacing, in pixels. If 'seeds'
#       image is provided, no grid is produced.
#   compactness: Compactness factor. Larger values cause
#       clusters to be more compact (square). Setting this to
#       0 disables spatial distance weighting.
#   connectivity: Connectivity.  Either 4 or 8.
#   neighborhoodSize: Tile neighborhood size (to avoid
#       tile boundary artifacts). Defaults to 2 * size.
#   seeds: If provided, any non-zero valued pixels are used as seed
#       locations. Pixels that touch (as specified by
#       'connectivity') are considered to belong to the same
#       cluster.
signatures.append({'args': [{'description': 'The input image for clustering.', 'name': 'image', 'type': 'Image'}, {'default': 5, 'description': "The superpixel seed location spacing, in pixels. If 'seeds' image is provided, no grid is produced.", 'name': 'size', 'optional': True, 'type': 'Integer'}, {'default': 1.0, 'description': 'Compactness factor. Larger values cause clusters to be more compact (square). Setting this to 0 disables spatial distance weighting.', 'name': 'compactness', 'optional': True, 'type': 'Float'}, {'default': 8, 'description': 'Connectivity.  Either 4 or 8.', 'name': 'connectivity', 'optional': True, 'type': 'Integer'}, {'default': None, 'description': 'Tile neighborhood size (to avoid tile boundary artifacts). Defaults to 2 * size.', 'name': 'neighborhoodSize', 'optional': True, 'type': 'Integer'}, {'default': None, 'description': "If provided, any non-zero valued pixels are used as seed locations. Pixels that touch (as specified by 'connectivity') are considered to belong to the same cluster.", 'name': 'seeds', 'optional': True, 'type': 'Image'}], 'description': "Superpixel clustering based on SNIC (Simple Non-Iterative Clustering). Outputs a band of cluster IDs and the per-cluster averages for each of the input bands. If the 'seeds' image isn't provided as input, the output will include a 'seeds' band containing the generated seed locations. See: Achanta, Radhakrishna and Susstrunk, Sabine, 'Superpixels and Polygons using Simple Non-Iterative Clustering', CVPR, 2017.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.Segmentation.SNIC'})
# Image.Segmentation.seedGrid
# Selects seed pixels for clustering.
#
# Args:
#   size: The superpixel seed location spacing, in pixels.
#   gridType: Type of grid. One of 'square' or 'hex'.
signatures.append({'args': [{'default': 5, 'description': 'The superpixel seed location spacing, in pixels.', 'name': 'size', 'optional': True, 'type': 'Integer'}, {'default': 'square', 'description': "Type of grid. One of 'square' or 'hex'.", 'name': 'gridType', 'optional': True, 'type': 'String'}], 'description': 'Selects seed pixels for clustering.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.Segmentation.seedGrid'})
# Image.abs
# Computes the absolute value of the input.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Computes the absolute value of the input.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.abs'})
# Image.acos
# Computes the arc cosine in radians of the input.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Computes the arc cosine in radians of the input.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.acos'})
# Image.add
# Adds the first value to the second for each matched pair of bands in image1
# and image2. If either image1 or image2 has only 1 band, then it is used
# against all the bands in the other image. If the images have the same
# number of bands, but not the same names, they're used pairwise in the
# natural order. The output bands are named for the longer of the two inputs,
# or if they're equal in length, in image1's order. The type of the output
# pixels is the union of the input types.
#
# Args:
#   image1: The image from which the left operand bands are taken.
#   image2: The image from which the right operand bands are taken.
signatures.append({'args': [{'description': 'The image from which the left operand bands are taken.', 'name': 'image1', 'type': 'Image'}, {'description': 'The image from which the right operand bands are taken.', 'name': 'image2', 'type': 'Image'}], 'description': "Adds the first value to the second for each matched pair of bands in image1 and image2. If either image1 or image2 has only 1 band, then it is used against all the bands in the other image. If the images have the same number of bands, but not the same names, they're used pairwise in the natural order. The output bands are named for the longer of the two inputs, or if they're equal in length, in image1's order. The type of the output pixels is the union of the input types.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.add'})
# Image.addBands
# Returns an image containing all bands copied from the first input and
# selected bands from the second input, optionally overwriting bands in the
# first image with the same name. The new image has the metadata and
# footprint from the first input image.
#
# Args:
#   dstImg: An image into which to copy bands.
#   srcImg: An image containing bands to copy.
#   names: Optional list of band names to copy. If names is omitted,
#       all bands from srcImg will be copied over.
#   overwrite: If true, bands from srcImg will override bands
#       with the same names in dstImg. Otherwise the new band
#       will be renamed with a numerical suffix ('foo' to
#       'foo_1' unless 'foo_1' exists, then 'foo_2' unless it
#       exists, etc).
signatures.append({'args': [{'description': 'An image into which to copy bands.', 'name': 'dstImg', 'type': 'Image'}, {'description': 'An image containing bands to copy.', 'name': 'srcImg', 'type': 'Image'}, {'default': None, 'description': 'Optional list of band names to copy. If names is omitted, all bands from srcImg will be copied over.', 'name': 'names', 'optional': True, 'type': 'List'}, {'default': False, 'description': "If true, bands from srcImg will override bands with the same names in dstImg. Otherwise the new band will be renamed with a numerical suffix ('foo' to 'foo_1' unless 'foo_1' exists, then 'foo_2' unless it exists, etc).", 'name': 'overwrite', 'optional': True, 'type': 'Boolean'}], 'description': 'Returns an image containing all bands copied from the first input and selected bands from the second input, optionally overwriting bands in the first image with the same name. The new image has the metadata and footprint from the first input image.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.addBands'})
# Image.and
# Returns 1 iff both values are non-zero for each matched pair of bands in
# image1 and image2. If either image1 or image2 has only 1 band, then it is
# used against all the bands in the other image. If the images have the same
# number of bands, but not the same names, they're used pairwise in the
# natural order. The output bands are named for the longer of the two inputs,
# or if they're equal in length, in image1's order. The type of the output
# pixels is boolean.
#
# Args:
#   image1: The image from which the left operand bands are taken.
#   image2: The image from which the right operand bands are taken.
signatures.append({'args': [{'description': 'The image from which the left operand bands are taken.', 'name': 'image1', 'type': 'Image'}, {'description': 'The image from which the right operand bands are taken.', 'name': 'image2', 'type': 'Image'}], 'description': "Returns 1 iff both values are non-zero for each matched pair of bands in image1 and image2. If either image1 or image2 has only 1 band, then it is used against all the bands in the other image. If the images have the same number of bands, but not the same names, they're used pairwise in the natural order. The output bands are named for the longer of the two inputs, or if they're equal in length, in image1's order. The type of the output pixels is boolean.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.And'})
# Image.annotate
# Adds an Annotation to an image.
#
# Args:
#   image: The input image.
#   annotation: The annotation to add to the image.
signatures.append({'args': [{'description': 'The input image.', 'name': 'image', 'type': 'Image'}, {'description': 'The annotation to add to the image.', 'name': 'annotation', 'type': 'Annotation'}], 'description': 'Adds an Annotation to an image.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.annotate'})
# Image.arrayAccum
# Accumulates elements of each array pixel along the given axis, by setting
# each element of the result array pixel to the reduction of elements in that
# pixel along the given axis, up to and including the current position on the
# axis. May be used to make a cumulative sum, a monotonically increasing
# sequence, etc.
#
# Args:
#   input: Input image.
#   axis: Axis along which to perform the cumulative sum.
#   reducer: Reducer to accumulate values. Default is SUM, to
#       produce the cumulative sum of each vector along the given
#       axis.
signatures.append({'args': [{'description': 'Input image.', 'name': 'input', 'type': 'Image'}, {'description': 'Axis along which to perform the cumulative sum.', 'name': 'axis', 'type': 'Integer'}, {'default': None, 'description': 'Reducer to accumulate values. Default is SUM, to produce the cumulative sum of each vector along the given axis.', 'name': 'reducer', 'optional': True, 'type': 'Reducer'}], 'description': 'Accumulates elements of each array pixel along the given axis, by setting each element of the result array pixel to the reduction of elements in that pixel along the given axis, up to and including the current position on the axis. May be used to make a cumulative sum, a monotonically increasing sequence, etc.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.arrayAccum'})
# Image.arrayCat
# Creates an array image by concatenating each array pixel along the given
# axis in each band.
#
# Args:
#   image1: First array image to concatenate.
#   image2: Second array image to concatenate.
#   axis: Axis to concatenate along.
signatures.append({'args': [{'description': 'First array image to concatenate.', 'name': 'image1', 'type': 'Image'}, {'description': 'Second array image to concatenate.', 'name': 'image2', 'type': 'Image'}, {'description': 'Axis to concatenate along.', 'name': 'axis', 'type': 'Integer'}], 'description': 'Creates an array image by concatenating each array pixel along the given axis in each band.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.arrayCat'})
# Image.arrayDimensions
# Returns the number of dimensions in each array band, and 0 for scalar image
# bands.
#
# Args:
#   input: Input image.
signatures.append({'args': [{'description': 'Input image.', 'name': 'input', 'type': 'Image'}], 'description': 'Returns the number of dimensions in each array band, and 0 for scalar image bands.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.arrayDimensions'})
# Image.arrayDotProduct
# Computes the dot product of each pair of 1-D arrays in the bands of the
# input images.
#
# Args:
#   image1: First array image of 1-D vectors.
#   image2: Second array image of 1-D vectors.
signatures.append({'args': [{'description': 'First array image of 1-D vectors.', 'name': 'image1', 'type': 'Image'}, {'description': 'Second array image of 1-D vectors.', 'name': 'image2', 'type': 'Image'}], 'description': 'Computes the dot product of each pair of 1-D arrays in the bands of the input images.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.arrayDotProduct'})
# Image.arrayFlatten
# Converts a single band image of equal-shape multidimensional pixels to an
# image of scalar pixels, with one band for each element of the array.
#
# Args:
#   image: Image of multidimensional pixels to flatten.
#   coordinateLabels: Name of each position along each
#       axis. For example, 2x2 arrays with axes meaning
#       'day' and 'color' could have labels like
#       [['monday', 'tuesday'], ['red', 'green']],
#       resulting in band names'monday_red',
#       'monday_green', 'tuesday_red', and
#       'tuesday_green'.
#   separator: Separator between array labels in each band name.
signatures.append({'args': [{'description': 'Image of multidimensional pixels to flatten.', 'name': 'image', 'type': 'Image'}, {'description': "Name of each position along each axis. For example, 2x2 arrays with axes meaning 'day' and 'color' could have labels like [['monday', 'tuesday'], ['red', 'green']], resulting in band names'monday_red', 'monday_green', 'tuesday_red', and 'tuesday_green'.", 'name': 'coordinateLabels', 'type': 'List'}, {'default': '_', 'description': 'Separator between array labels in each band name.', 'name': 'separator', 'optional': True, 'type': 'String'}], 'description': 'Converts a single band image of equal-shape multidimensional pixels to an image of scalar pixels, with one band for each element of the array.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.arrayFlatten'})
# Image.arrayGet
# For each band, an output band of the same name is created with the value at
# the given position extracted from the input multidimensional pixel in that
# band.
#
# Args:
#   image: Array to get an element from.
#   position: The coordinates of the element to get. There must
#       be as many scalar bands as there are dimensions in the
#       input image.
signatures.append({'args': [{'description': 'Array to get an element from.', 'name': 'image', 'type': 'Image'}, {'description': 'The coordinates of the element to get. There must be as many scalar bands as there are dimensions in the input image.', 'name': 'position', 'type': 'Image'}], 'description': 'For each band, an output band of the same name is created with the value at the given position extracted from the input multidimensional pixel in that band.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.arrayGet'})
# Image.arrayLength
# Returns the length of each pixel's array along the given axis.
#
# Args:
#   input: Input image.
#   axis: The axis along which to take the length.
signatures.append({'args': [{'description': 'Input image.', 'name': 'input', 'type': 'Image'}, {'description': 'The axis along which to take the length.', 'name': 'axis', 'type': 'Integer'}], 'description': "Returns the length of each pixel's array along the given axis.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.arrayLength'})
# Image.arrayLengths
# Returns a 1D array image with the length of each array axis.
#
# Args:
#   input: Input image.
signatures.append({'args': [{'description': 'Input image.', 'name': 'input', 'type': 'Image'}], 'description': 'Returns a 1D array image with the length of each array axis.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.arrayLengths'})
# Image.arrayMask
# Creates an array image where each array-valued pixel is masked with another
# array-valued pixel, retaining only the elements where the mask is non-zero.
# If the mask image has one band it will be applied to all the bands of
# 'input', otherwise they must have the same number of bands.
#
# Args:
#   input: Array image to mask.
#   mask: Array image to mask with.
signatures.append({'args': [{'description': 'Array image to mask.', 'name': 'input', 'type': 'Image'}, {'description': 'Array image to mask with.', 'name': 'mask', 'type': 'Image'}], 'description': "Creates an array image where each array-valued pixel is masked with another array-valued pixel, retaining only the elements where the mask is non-zero. If the mask image has one band it will be applied to all the bands of 'input', otherwise they must have the same number of bands.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.arrayMask'})
# Image.arrayProject
# Projects the array in each pixel to a lower dimensional space by specifying
# the axes to retain. Dropped axes must be at most length 1.
#
# Args:
#   input: Input image.
#   axes: The axes to retain. Other axes will be discarded and must
#       be at most length 1.
signatures.append({'args': [{'description': 'Input image.', 'name': 'input', 'type': 'Image'}, {'description': 'The axes to retain. Other axes will be discarded and must be at most length 1.', 'name': 'axes', 'type': 'List'}], 'description': 'Projects the array in each pixel to a lower dimensional space by specifying the axes to retain. Dropped axes must be at most length 1.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.arrayProject'})
# Image.arrayReduce
# Reduces elements of each array pixel.
#
# Args:
#   input: Input image.
#   reducer: The reducer to apply
#   axes: The list of array axes to reduce in each pixel.  The output
#       will have a length of 1 in all these axes.
#   fieldAxis: The axis for the reducer's input and output
#       fields.  Only required if the reducer has multiple
#       inputs or outputs.
signatures.append({'args': [{'description': 'Input image.', 'name': 'input', 'type': 'Image'}, {'description': 'The reducer to apply', 'name': 'reducer', 'type': 'Reducer'}, {'description': 'The list of array axes to reduce in each pixel.  The output will have a length of 1 in all these axes.', 'name': 'axes', 'type': 'List'}, {'default': None, 'description': "The axis for the reducer's input and output fields.  Only required if the reducer has multiple inputs or outputs.", 'name': 'fieldAxis', 'optional': True, 'type': 'Integer'}], 'description': 'Reduces elements of each array pixel.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.arrayReduce'})
# Image.arrayRepeat
# Repeats each array pixel along the given axis. Each output pixel will have
# the shape of the input pixel, except length along the repeated axis, which
# will be multiplied by the number of copies.
#
# Args:
#   input: Image of array pixels to be repeated.
#   axis: Axis along which to repeat each pixel's array.
#   copies: Number of copies of each pixel.
signatures.append({'args': [{'description': 'Image of array pixels to be repeated.', 'name': 'input', 'type': 'Image'}, {'description': "Axis along which to repeat each pixel's array.", 'name': 'axis', 'type': 'Integer'}, {'description': 'Number of copies of each pixel.', 'name': 'copies', 'type': 'Image'}], 'description': 'Repeats each array pixel along the given axis. Each output pixel will have the shape of the input pixel, except length along the repeated axis, which will be multiplied by the number of copies.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.arrayRepeat'})
# Image.arraySlice
# Creates a subarray by slicing out each position along the given axis from
# the 'start' (inclusive) to 'end' (exclusive) by increments of 'step'. The
# result will have as many dimensions as the input, and the same length in
# all directions except the slicing axis, where the length will be the number
# of positions from 'start' to 'end' by 'step' that are in range of the input
# array's length along 'axis'. This means the result can be length 0 along
# the given axis if start=end, or if the start or end values are entirely out
# of range.
#
# Args:
#   input: Input array image.
#   axis: Axis to subset.
#   start: The coordinate of the first slice (inclusive) along
#       'axis'. Negative numbers are used to position the start of
#       slicing relative to the end of the array, where -1 starts at
#       the last position on the axis, -2 starts at the next to last
#       position, etc. There must one band for start indices, or one
#       band per 'input' band. If this argument is not set or masked
#       at some pixel, then the slice at that pixel will start at
#       index 0.
#   end: The coordinate (exclusive) at which to stop taking slices. By
#       default this will be the length of the given axis. Negative
#       numbers are used to position the end of slicing relative to
#       the end of the array, where -1 will exclude the last position,
#       -2 will exclude the last two positions, etc. There must be one
#       band for end indices, or one band per 'input' band. If this
#       argument is not set or masked at some pixel, then the slice at
#       that pixel will end just after the last index.
#   step: The separation between slices along 'axis'; a slice will be
#       taken at each whole multiple of 'step' from 'start'
#       (inclusive) to 'end' (exclusive). Must be positive.
signatures.append({'args': [{'description': 'Input array image.', 'name': 'input', 'type': 'Image'}, {'default': 0, 'description': 'Axis to subset.', 'name': 'axis', 'optional': True, 'type': 'Integer'}, {'default': None, 'description': "The coordinate of the first slice (inclusive) along 'axis'. Negative numbers are used to position the start of slicing relative to the end of the array, where -1 starts at the last position on the axis, -2 starts at the next to last position, etc. There must one band for start indices, or one band per 'input' band. If this argument is not set or masked at some pixel, then the slice at that pixel will start at index 0.", 'name': 'start', 'optional': True, 'type': 'Image'}, {'default': None, 'description': "The coordinate (exclusive) at which to stop taking slices. By default this will be the length of the given axis. Negative numbers are used to position the end of slicing relative to the end of the array, where -1 will exclude the last position, -2 will exclude the last two positions, etc. There must be one band for end indices, or one band per 'input' band. If this argument is not set or masked at some pixel, then the slice at that pixel will end just after the last index.", 'name': 'end', 'optional': True, 'type': 'Image'}, {'default': 1, 'description': "The separation between slices along 'axis'; a slice will be taken at each whole multiple of 'step' from 'start' (inclusive) to 'end' (exclusive). Must be positive.", 'name': 'step', 'optional': True, 'type': 'Integer'}], 'description': "Creates a subarray by slicing out each position along the given axis from the 'start' (inclusive) to 'end' (exclusive) by increments of 'step'. The result will have as many dimensions as the input, and the same length in all directions except the slicing axis, where the length will be the number of positions from 'start' to 'end' by 'step' that are in range of the input array's length along 'axis'. This means the result can be length 0 along the given axis if start=end, or if the start or end values are entirely out of range.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.arraySlice'})
# Image.arraySort
# Sorts elements of each array pixel along one axis.
#
# Args:
#   image: Array image to sort.
#   keys: Optional keys to sort by. If not provided, the values are
#       used as the keys. The keys can only have multiple elements
#       along one axis, which determines the direction to sort in.
signatures.append({'args': [{'description': 'Array image to sort.', 'name': 'image', 'type': 'Image'}, {'default': None, 'description': 'Optional keys to sort by. If not provided, the values are used as the keys. The keys can only have multiple elements along one axis, which determines the direction to sort in.', 'name': 'keys', 'optional': True, 'type': 'Image'}], 'description': 'Sorts elements of each array pixel along one axis.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.arraySort'})
# Image.arrayTranspose
# Transposes two dimensions of each array pixel.
#
# Args:
#   input: Input image.
#   axis1: First axis to swap.
#   axis2: Second axis to swap.
signatures.append({'args': [{'description': 'Input image.', 'name': 'input', 'type': 'Image'}, {'default': 0, 'description': 'First axis to swap.', 'name': 'axis1', 'optional': True, 'type': 'Integer'}, {'default': 1, 'description': 'Second axis to swap.', 'name': 'axis2', 'optional': True, 'type': 'Integer'}], 'description': 'Transposes two dimensions of each array pixel.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.arrayTranspose'})
# Image.asin
# Computes the arc sine in radians of the input.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Computes the arc sine in radians of the input.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.asin'})
# Image.atan
# Computes the arc tangent in radians of the input.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Computes the arc tangent in radians of the input.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.atan'})
# Image.atan2
# Calculates the angle formed by the 2D vector [x, y] for each matched pair
# of bands in image1 and image2. If either image1 or image2 has only 1 band,
# then it is used against all the bands in the other image. If the images
# have the same number of bands, but not the same names, they're used
# pairwise in the natural order. The output bands are named for the longer of
# the two inputs, or if they're equal in length, in image1's order. The type
# of the output pixels is float.
#
# Args:
#   image1: The image from which the left operand bands are taken.
#   image2: The image from which the right operand bands are taken.
signatures.append({'args': [{'description': 'The image from which the left operand bands are taken.', 'name': 'image1', 'type': 'Image'}, {'description': 'The image from which the right operand bands are taken.', 'name': 'image2', 'type': 'Image'}], 'description': "Calculates the angle formed by the 2D vector [x, y] for each matched pair of bands in image1 and image2. If either image1 or image2 has only 1 band, then it is used against all the bands in the other image. If the images have the same number of bands, but not the same names, they're used pairwise in the natural order. The output bands are named for the longer of the two inputs, or if they're equal in length, in image1's order. The type of the output pixels is float.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.atan2'})
# Image.bandNames
# Returns a list containing the names of the bands of an image.
#
# Args:
#   image: The image from which to get band names.
signatures.append({'args': [{'description': 'The image from which to get band names.', 'name': 'image', 'type': 'Image'}], 'description': 'Returns a list containing the names of the bands of an image.', 'returns': 'List', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.bandNames'})
# Image.bandTypes
# Returns a dictionary of the image's band types.
#
# Args:
#   image: The image from which to get band types.
signatures.append({'args': [{'description': 'The image from which to get band types.', 'name': 'image', 'type': 'Image'}], 'description': "Returns a dictionary of the image's band types.", 'returns': 'Dictionary', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.bandTypes'})
# Image.bitCount
# Calculates the number of one-bits in the 64-bit two's complement binary
# representation of the input.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': "Calculates the number of one-bits in the 64-bit two's complement binary representation of the input.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.bitCount'})
# Image.bitsToArrayImage
# Turns the bits of an integer into a 1-D array.  The array has a lengthup to
# the highest 'on' bit in the input.
#
# Args:
#   input: Input image.
signatures.append({'args': [{'description': 'Input image.', 'name': 'input', 'type': 'Image'}], 'description': "Turns the bits of an integer into a 1-D array.  The array has a lengthup to the highest 'on' bit in the input.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.bitsToArrayImage'})
# Image.bitwiseAnd
# Calculates the bitwise AND of the input values for each matched pair of
# bands in image1 and image2. If either image1 or image2 has only 1 band,
# then it is used against all the bands in the other image. If the images
# have the same number of bands, but not the same names, they're used
# pairwise in the natural order. The output bands are named for the longer of
# the two inputs, or if they're equal in length, in image1's order. The type
# of the output pixels is the union of the input types.
#
# Args:
#   image1: The image from which the left operand bands are taken.
#   image2: The image from which the right operand bands are taken.
signatures.append({'args': [{'description': 'The image from which the left operand bands are taken.', 'name': 'image1', 'type': 'Image'}, {'description': 'The image from which the right operand bands are taken.', 'name': 'image2', 'type': 'Image'}], 'description': "Calculates the bitwise AND of the input values for each matched pair of bands in image1 and image2. If either image1 or image2 has only 1 band, then it is used against all the bands in the other image. If the images have the same number of bands, but not the same names, they're used pairwise in the natural order. The output bands are named for the longer of the two inputs, or if they're equal in length, in image1's order. The type of the output pixels is the union of the input types.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.bitwiseAnd'})
# Image.bitwiseNot
# Calculates the bitwise NOT of the input, in the smallest signed integer
# type that can hold the input.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Calculates the bitwise NOT of the input, in the smallest signed integer type that can hold the input.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.bitwiseNot'})
# Image.bitwiseOr
# Calculates the bitwise OR of the input values for each matched pair of
# bands in image1 and image2. If either image1 or image2 has only 1 band,
# then it is used against all the bands in the other image. If the images
# have the same number of bands, but not the same names, they're used
# pairwise in the natural order. The output bands are named for the longer of
# the two inputs, or if they're equal in length, in image1's order. The type
# of the output pixels is the union of the input types.
#
# Args:
#   image1: The image from which the left operand bands are taken.
#   image2: The image from which the right operand bands are taken.
signatures.append({'args': [{'description': 'The image from which the left operand bands are taken.', 'name': 'image1', 'type': 'Image'}, {'description': 'The image from which the right operand bands are taken.', 'name': 'image2', 'type': 'Image'}], 'description': "Calculates the bitwise OR of the input values for each matched pair of bands in image1 and image2. If either image1 or image2 has only 1 band, then it is used against all the bands in the other image. If the images have the same number of bands, but not the same names, they're used pairwise in the natural order. The output bands are named for the longer of the two inputs, or if they're equal in length, in image1's order. The type of the output pixels is the union of the input types.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.bitwiseOr'})
# Image.bitwiseXor
# Calculates the bitwise XOR of the input values for each matched pair of
# bands in image1 and image2. If either image1 or image2 has only 1 band,
# then it is used against all the bands in the other image. If the images
# have the same number of bands, but not the same names, they're used
# pairwise in the natural order. The output bands are named for the longer of
# the two inputs, or if they're equal in length, in image1's order. The type
# of the output pixels is the union of the input types.
#
# Args:
#   image1: The image from which the left operand bands are taken.
#   image2: The image from which the right operand bands are taken.
signatures.append({'args': [{'description': 'The image from which the left operand bands are taken.', 'name': 'image1', 'type': 'Image'}, {'description': 'The image from which the right operand bands are taken.', 'name': 'image2', 'type': 'Image'}], 'description': "Calculates the bitwise XOR of the input values for each matched pair of bands in image1 and image2. If either image1 or image2 has only 1 band, then it is used against all the bands in the other image. If the images have the same number of bands, but not the same names, they're used pairwise in the natural order. The output bands are named for the longer of the two inputs, or if they're equal in length, in image1's order. The type of the output pixels is the union of the input types.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.bitwiseXor'})
# Image.bitwise_and
# Calculates the bitwise AND of the input values for each matched pair of
# bands in image1 and image2. If either image1 or image2 has only 1 band,
# then it is used against all the bands in the other image. If the images
# have the same number of bands, but not the same names, they're used
# pairwise in the natural order. The output bands are named for the longer of
# the two inputs, or if they're equal in length, in image1's order. The type
# of the output pixels is the union of the input types.
#
# Args:
#   image1: The image from which the left operand bands are taken.
#   image2: The image from which the right operand bands are taken.
signatures.append({'args': [{'description': 'The image from which the left operand bands are taken.', 'name': 'image1', 'type': 'Image'}, {'description': 'The image from which the right operand bands are taken.', 'name': 'image2', 'type': 'Image'}], 'description': "Calculates the bitwise AND of the input values for each matched pair of bands in image1 and image2. If either image1 or image2 has only 1 band, then it is used against all the bands in the other image. If the images have the same number of bands, but not the same names, they're used pairwise in the natural order. The output bands are named for the longer of the two inputs, or if they're equal in length, in image1's order. The type of the output pixels is the union of the input types.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.bitwise_and'})
# Image.bitwise_not
# Calculates the bitwise NOT of the input, in the smallest signed integer
# type that can hold the input.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Calculates the bitwise NOT of the input, in the smallest signed integer type that can hold the input.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.bitwise_not'})
# Image.bitwise_or
# Calculates the bitwise OR of the input values for each matched pair of
# bands in image1 and image2. If either image1 or image2 has only 1 band,
# then it is used against all the bands in the other image. If the images
# have the same number of bands, but not the same names, they're used
# pairwise in the natural order. The output bands are named for the longer of
# the two inputs, or if they're equal in length, in image1's order. The type
# of the output pixels is the union of the input types.
#
# Args:
#   image1: The image from which the left operand bands are taken.
#   image2: The image from which the right operand bands are taken.
signatures.append({'args': [{'description': 'The image from which the left operand bands are taken.', 'name': 'image1', 'type': 'Image'}, {'description': 'The image from which the right operand bands are taken.', 'name': 'image2', 'type': 'Image'}], 'description': "Calculates the bitwise OR of the input values for each matched pair of bands in image1 and image2. If either image1 or image2 has only 1 band, then it is used against all the bands in the other image. If the images have the same number of bands, but not the same names, they're used pairwise in the natural order. The output bands are named for the longer of the two inputs, or if they're equal in length, in image1's order. The type of the output pixels is the union of the input types.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.bitwise_or'})
# Image.bitwise_xor
# Calculates the bitwise XOR of the input values for each matched pair of
# bands in image1 and image2. If either image1 or image2 has only 1 band,
# then it is used against all the bands in the other image. If the images
# have the same number of bands, but not the same names, they're used
# pairwise in the natural order. The output bands are named for the longer of
# the two inputs, or if they're equal in length, in image1's order. The type
# of the output pixels is the union of the input types.
#
# Args:
#   image1: The image from which the left operand bands are taken.
#   image2: The image from which the right operand bands are taken.
signatures.append({'args': [{'description': 'The image from which the left operand bands are taken.', 'name': 'image1', 'type': 'Image'}, {'description': 'The image from which the right operand bands are taken.', 'name': 'image2', 'type': 'Image'}], 'description': "Calculates the bitwise XOR of the input values for each matched pair of bands in image1 and image2. If either image1 or image2 has only 1 band, then it is used against all the bands in the other image. If the images have the same number of bands, but not the same names, they're used pairwise in the natural order. The output bands are named for the longer of the two inputs, or if they're equal in length, in image1's order. The type of the output pixels is the union of the input types.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.bitwise_xor'})
# Image.blend
# Overlays one image on top of another. The images are blended together using
# the masks as opacity. If either of images has only 1 band, it is replicated
# to match the number of bands in the other image.
#
# Args:
#   bottom: The bottom image.
#   top: The top image.
signatures.append({'args': [{'description': 'The bottom image.', 'name': 'bottom', 'type': 'Image'}, {'description': 'The top image.', 'name': 'top', 'type': 'Image'}], 'description': 'Overlays one image on top of another. The images are blended together using the masks as opacity. If either of images has only 1 band, it is replicated to match the number of bands in the other image.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.blend'})
# Image.byte
# Casts the input value to an unsigned 8-bit integer.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Casts the input value to an unsigned 8-bit integer.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.byte'})
# Image.cast
# Casts some or all bands of an image to the specified types.
#
# Args:
#   image: The image to cast.
#   bandTypes: A dictionary from band name to band types. Types
#       can be PixelTypes or strings. The valid strings are:
#       'int8', 'int16', 'int32', 'int64', 'uint8', 'uint16',
#       'uint32', 'byte', 'short', 'int', 'long', 'float' and
#       'double'. If bandTypes includes bands that are not
#       already in the input image, they will be added to the
#       image as transparent bands. If bandOrder isn't also
#       specified, new bands will be appended in alphabetical
#       order.
#   bandOrder: A list specifying the order of the bands in the
#       result. If specified, must match the full list of bands
#       in the result.
signatures.append({'args': [{'description': 'The image to cast.', 'name': 'image', 'type': 'Image'}, {'description': "A dictionary from band name to band types. Types can be PixelTypes or strings. The valid strings are: 'int8', 'int16', 'int32', 'int64', 'uint8', 'uint16', 'uint32', 'byte', 'short', 'int', 'long', 'float' and 'double'. If bandTypes includes bands that are not already in the input image, they will be added to the image as transparent bands. If bandOrder isn't also specified, new bands will be appended in alphabetical order.", 'name': 'bandTypes', 'type': 'Dictionary'}, {'default': None, 'description': 'A list specifying the order of the bands in the result. If specified, must match the full list of bands in the result.', 'name': 'bandOrder', 'optional': True, 'type': 'List'}], 'description': 'Casts some or all bands of an image to the specified types.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.cast'})
# Image.cbrt
# Computes the cubic root of the input.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Computes the cubic root of the input.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.cbrt'})
# Image.ceil
# Computes the smallest integer greater than or equal to the input.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Computes the smallest integer greater than or equal to the input.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.ceil'})
# Image.changeProj
# Tweaks the projection of the input image, moving each pixel from its
# location in srcProj to the same coordinates in dstProj.
#
# Args:
#   input
#   srcProj: The original projection.
#   dstProj: The new projection.
signatures.append({'args': [{'name': 'input', 'type': 'Image'}, {'description': 'The original projection.', 'name': 'srcProj', 'type': 'Projection'}, {'description': 'The new projection.', 'name': 'dstProj', 'type': 'Projection'}], 'description': 'Tweaks the projection of the input image, moving each pixel from its location in srcProj to the same coordinates in dstProj.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.changeProj'})
# Image.clamp
# Clamps the values in all bands of an image to all lie within the specified
# range.
#
# Args:
#   input: The image to clamp.
#   low: The minimum allowed value in the range.
#   high: The maximum allowed value in the range.
signatures.append({'args': [{'description': 'The image to clamp.', 'name': 'input', 'type': 'Image'}, {'description': 'The minimum allowed value in the range.', 'name': 'low', 'type': 'Float'}, {'description': 'The maximum allowed value in the range.', 'name': 'high', 'type': 'Float'}], 'description': 'Clamps the values in all bands of an image to all lie within the specified range.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.clamp'})
# Image.classify
# Classifies an image.
#
# Args:
#   image: The image to classify.  Bands are extracted from this
#       image by name, and it must contain all the bands named in
#       the classifier's schema.
#   classifier: The classifier to use.
#   outputName: The name of the band to be added.
signatures.append({'args': [{'description': "The image to classify.  Bands are extracted from this image by name, and it must contain all the bands named in the classifier's schema.", 'name': 'image', 'type': 'Image'}, {'description': 'The classifier to use.', 'name': 'classifier', 'type': 'Object'}, {'default': 'classification', 'description': 'The name of the band to be added.', 'name': 'outputName', 'optional': True, 'type': 'String'}], 'description': 'Classifies an image.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.classify'})
# Image.clip
# Clips an image to a Geometry or Feature (use clipToCollection to clip an
# image to a FeatureCollection). The output bands correspond exactly the
# input bands, except data not covered by the geometry is masked.  The output
# image retains the metadata of the input image.
#
# Args:
#   input: The image to clip.
#   geometry: The Geometry or Feature to clip to.
signatures.append({'args': [{'description': 'The image to clip.', 'name': 'input', 'type': 'Image'}, {'default': None, 'description': 'The Geometry or Feature to clip to.', 'name': 'geometry', 'optional': True, 'type': 'Object'}], 'description': 'Clips an image to a Geometry or Feature (use clipToCollection to clip an image to a FeatureCollection). The output bands correspond exactly the input bands, except data not covered by the geometry is masked.  The output image retains the metadata of the input image.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.clip'})
# Image.clipToCollection
# Clips an image to a FeatureCollection. The output bands correspond exactly
# the input bands, except data not covered by the geometry of at least one
# feature from the collection is masked. The output image retains the
# metadata of the input image.
#
# Args:
#   input: The image to clip.
#   collection: The FeatureCollection to clip to.
signatures.append({'args': [{'description': 'The image to clip.', 'name': 'input', 'type': 'Image'}, {'description': 'The FeatureCollection to clip to.', 'name': 'collection', 'type': 'Object'}], 'description': 'Clips an image to a FeatureCollection. The output bands correspond exactly the input bands, except data not covered by the geometry of at least one feature from the collection is masked. The output image retains the metadata of the input image.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.clipToCollection'})
# Image.cluster
# Applies a clusterer to an image.  Returns a new image with a single band
# containing values from 0 to N, indicating the cluster each pixel is
# assigned to.
#
# Args:
#   image: The image to cluster. Must contain all the bands in the
#       clusterer's schema.
#   clusterer: The clusterer to use.
#   outputName: The name of the output band.
signatures.append({'args': [{'description': "The image to cluster. Must contain all the bands in the clusterer's schema.", 'name': 'image', 'type': 'Image'}, {'description': 'The clusterer to use.', 'name': 'clusterer', 'type': 'Clusterer'}, {'default': 'cluster', 'description': 'The name of the output band.', 'name': 'outputName', 'optional': True, 'type': 'String'}], 'description': 'Applies a clusterer to an image.  Returns a new image with a single band containing values from 0 to N, indicating the cluster each pixel is assigned to.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.cluster'})
# Image.connectedComponents
# Finds connected components with the same value of the first band of the
# input and labels them with a globally unique value.  Connectedness is
# specified by the given kernel.  Objects larger than maxSize are considered
# background, and are masked.
#
# Args:
#   image: The image to label.
#   connectedness: Connectedness kernel.
#   maxSize: Maximum size of objects to be labeled.
signatures.append({'args': [{'description': 'The image to label.', 'name': 'image', 'type': 'Image'}, {'description': 'Connectedness kernel.', 'name': 'connectedness', 'type': 'Kernel'}, {'description': 'Maximum size of objects to be labeled.', 'name': 'maxSize', 'type': 'Integer'}], 'description': 'Finds connected components with the same value of the first band of the input and labels them with a globally unique value.  Connectedness is specified by the given kernel.  Objects larger than maxSize are considered background, and are masked.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.connectedComponents'})
# Image.connectedPixelCount
# Generate an image where each pixel contains the number of 4- or 8-connected
# neighbors (including itself).
#
# Args:
#   input: The input image.
#   maxSize: The maximum size of the neighborhood in pixels.
#   eightConnected: Whether to use 8-connected rather
#       4-connected rules.
signatures.append({'args': [{'description': 'The input image.', 'name': 'input', 'type': 'Image'}, {'default': 100, 'description': 'The maximum size of the neighborhood in pixels.', 'name': 'maxSize', 'optional': True, 'type': 'Integer'}, {'default': True, 'description': 'Whether to use 8-connected rather 4-connected rules.', 'name': 'eightConnected', 'optional': True, 'type': 'Boolean'}], 'description': 'Generate an image where each pixel contains the number of 4- or 8-connected neighbors (including itself).', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.connectedPixelCount'})
# Image.constant
# Generates an image containing a constant value everywhere.
#
# Args:
#   value: The value of the pixels in the constant image. Must be a
#       number or an Array or a list of numbers or Arrays.
signatures.append({'args': [{'description': 'The value of the pixels in the constant image. Must be a number or an Array or a list of numbers or Arrays.', 'name': 'value', 'type': 'Object'}], 'description': 'Generates an image containing a constant value everywhere.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.constant'})
# Image.convolve
# Convolves each band of an image with the given kernel.
#
# Args:
#   image: The image to convolve.
#   kernel: The kernel to convolve with.
signatures.append({'args': [{'description': 'The image to convolve.', 'name': 'image', 'type': 'Image'}, {'description': 'The kernel to convolve with.', 'name': 'kernel', 'type': 'Kernel'}], 'description': 'Convolves each band of an image with the given kernel.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.convolve'})
# Image.copyProperties
# Copies metadata properties from one element to another.
#
# Args:
#   destination: The object whose properties to override.
#   source: The object from which to copy the properties.
#   properties: The properties to copy.  If omitted, all
#       ordinary (i.e. non-system) properties are copied.
#   exclude: The list of properties to exclude when copying all
#       properties. Must not be specified if properties is.
signatures.append({'args': [{'default': None, 'description': 'The object whose properties to override.', 'name': 'destination', 'optional': True, 'type': 'Element'}, {'default': None, 'description': 'The object from which to copy the properties.', 'name': 'source', 'optional': True, 'type': 'Element'}, {'default': None, 'description': 'The properties to copy.  If omitted, all ordinary (i.e. non-system) properties are copied.', 'name': 'properties', 'optional': True, 'type': 'List'}, {'default': None, 'description': 'The list of properties to exclude when copying all properties. Must not be specified if properties is.', 'name': 'exclude', 'optional': True, 'type': 'List'}], 'description': 'Copies metadata properties from one element to another.', 'returns': 'Element', 'type': 'Algorithm', 'hidden': False, 'deprecated': 'Use Element.copyProperties()', 'name': 'Image.copyProperties'})
# Image.cos
# Computes the cosine of the input in radians.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Computes the cosine of the input in radians.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.cos'})
# Image.cosh
# Computes the hyperbolic cosine of the input.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Computes the hyperbolic cosine of the input.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.cosh'})
# Image.cumulativeCost
# Computes a cumulative cost map based on an image containing costs to
# traverse each pixel and an image containing source locations.
#
# Args:
#   cost: A single-band image representing the cost to traverse each
#       pixel. Masked pixels can't be traversed.
#   source: A single-band image representing the sources. A pixel
#       value different from 0  defines a source pixel.
#   maxDistance: Maximum distance for computation, in meters.
#   geodeticDistance: If true, geodetic distance along
#       the curved surface is used, assuming a spherical
#       Earth of radius 6378137.0. If false, euclidean
#       distance in the 2D plane of the map projection is
#       used (faster, but less accurate).
signatures.append({'args': [{'description': "A single-band image representing the cost to traverse each pixel. Masked pixels can't be traversed.", 'name': 'cost', 'type': 'Image'}, {'description': 'A single-band image representing the sources. A pixel value different from 0  defines a source pixel.', 'name': 'source', 'type': 'Image'}, {'description': 'Maximum distance for computation, in meters.', 'name': 'maxDistance', 'type': 'Float'}, {'default': True, 'description': 'If true, geodetic distance along the curved surface is used, assuming a spherical Earth of radius 6378137.0. If false, euclidean distance in the 2D plane of the map projection is used (faster, but less accurate).', 'name': 'geodeticDistance', 'optional': True, 'type': 'Boolean'}], 'description': 'Computes a cumulative cost map based on an image containing costs to traverse each pixel and an image containing source locations.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.cumulativeCost'})
# Image.date
# Returns the acquisition time of an image as a Date object.  This helper
# function is equivalent to ee.Date(image.get('system:time_start')).
#
# Args:
#   image: The image whose acquisition time to return.
signatures.append({'args': [{'description': 'The image whose acquisition time to return.', 'name': 'image', 'type': 'Image'}], 'description': "Returns the acquisition time of an image as a Date object.  This helper function is equivalent to ee.Date(image.get('system:time_start')).", 'returns': 'Date', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.date'})
# Image.derivative
# Computes the X and Y discrete derivatives for each band in the input image,
# in pixel coordinates.
#
# Args:
#   image: The input image.
signatures.append({'args': [{'description': 'The input image.', 'name': 'image', 'type': 'Image'}], 'description': 'Computes the X and Y discrete derivatives for each band in the input image, in pixel coordinates.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.derivative'})
# Image.digamma
# Computes the digamma function of the input.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Computes the digamma function of the input.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.digamma'})
# Image.displace
# Warps an image using an image of displacements.
#
# Args:
#   image: The image to warp.
#   displacement: An image containing displacement values.
#       The first band is interpreted as the 'X' displacement
#       and the second as the 'Y' displacement. Each
#       displacement pixel is a [dx,dy] vector added to the
#       pixel location to determine the corresponding pixel
#       location in 'image'. Displacements are interpreted as
#       meters in the default projection of the displacement
#       image.
#   mode: The interpolation mode to use.  One of 'nearest_neighbor',
#       'bilinear' or 'bicubic'.)
signatures.append({'args': [{'description': 'The image to warp.', 'name': 'image', 'type': 'Image'}, {'description': "An image containing displacement values. The first band is interpreted as the 'X' displacement and the second as the 'Y' displacement. Each displacement pixel is a [dx,dy] vector added to the pixel location to determine the corresponding pixel location in 'image'. Displacements are interpreted as meters in the default projection of the displacement image.", 'name': 'displacement', 'type': 'Image'}, {'default': 'bicubic', 'description': "The interpolation mode to use.  One of 'nearest_neighbor', 'bilinear' or 'bicubic'.)", 'name': 'mode', 'optional': True, 'type': 'String'}], 'description': 'Warps an image using an image of displacements.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.displace'})
# Image.displacement
# Determines displacements required to register an image to a reference image
# while allowing local, rubber sheet deformations. Displacements are computed
# in the CRS of the reference image, at a scale dictated by the lowest
# resolution of the following three projections: input image projection,
# reference image projection, and requested projection. The displacements are
# then transformed into the user-specified projection for output.
#
# Args:
#   image: The image to register.
#   referenceImage: The image to register to.
#   maxOffset: The maximum offset allowed when attempting to
#       align the input images, in meters. Using a smaller value
#       can reduce computation time significantly, but it must
#       still be large enough to cover the greatest displacement
#       within the entire image region.
#   projection: The projection in which to output displacement
#       values. The default is the projection of the first band
#       of the reference image.
#   patchWidth: Patch size for detecting image offsets, in
#       meters. This should be set large enough to capture
#       texture, as well as large enough that ignorable objects
#       are small within the patch. Default is null. Patch size
#       will be determined automatically if not provided.
#   stiffness: Enforces a stiffness constraint on the solution.
#       Valid values are in the range [0,10]. The stiffness is
#       used for outlier rejection when determining
#       displacements at adjacent grid points. Higher values
#       move the solution towards a rigid transformation. Lower
#       values allow more distortion or warping of the image
#       during registration.
signatures.append({'args': [{'description': 'The image to register.', 'name': 'image', 'type': 'Image'}, {'description': 'The image to register to.', 'name': 'referenceImage', 'type': 'Image'}, {'description': 'The maximum offset allowed when attempting to align the input images, in meters. Using a smaller value can reduce computation time significantly, but it must still be large enough to cover the greatest displacement within the entire image region.', 'name': 'maxOffset', 'type': 'Float'}, {'default': None, 'description': 'The projection in which to output displacement values. The default is the projection of the first band of the reference image.', 'name': 'projection', 'optional': True, 'type': 'Projection'}, {'default': None, 'description': 'Patch size for detecting image offsets, in meters. This should be set large enough to capture texture, as well as large enough that ignorable objects are small within the patch. Default is null. Patch size will be determined automatically if not provided.', 'name': 'patchWidth', 'optional': True, 'type': 'Float'}, {'default': 5.0, 'description': 'Enforces a stiffness constraint on the solution. Valid values are in the range [0,10]. The stiffness is used for outlier rejection when determining displacements at adjacent grid points. Higher values move the solution towards a rigid transformation. Lower values allow more distortion or warping of the image during registration.', 'name': 'stiffness', 'optional': True, 'type': 'Float'}], 'description': 'Determines displacements required to register an image to a reference image while allowing local, rubber sheet deformations. Displacements are computed in the CRS of the reference image, at a scale dictated by the lowest resolution of the following three projections: input image projection, reference image projection, and requested projection. The displacements are then transformed into the user-specified projection for output.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.displacement'})
# Image.distance
# Computes the distance to the nearest non-zero pixel in each band, using the
# specified distance kernel.
#
# Args:
#   image: The input image.
#   kernel: The distance kernel.
#   skipMasked: Mask output pixels if the corresponding input
#       pixel is masked.
signatures.append({'args': [{'description': 'The input image.', 'name': 'image', 'type': 'Image'}, {'default': None, 'description': 'The distance kernel.', 'name': 'kernel', 'optional': True, 'type': 'Kernel'}, {'default': True, 'description': 'Mask output pixels if the corresponding input pixel is masked.', 'name': 'skipMasked', 'optional': True, 'type': 'Boolean'}], 'description': 'Computes the distance to the nearest non-zero pixel in each band, using the specified distance kernel.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.distance'})
# Image.divide
# Divides the first value by the second, returning 0 for division by 0 for
# each matched pair of bands in image1 and image2. If either image1 or image2
# has only 1 band, then it is used against all the bands in the other image.
# If the images have the same number of bands, but not the same names,
# they're used pairwise in the natural order. The output bands are named for
# the longer of the two inputs, or if they're equal in length, in image1's
# order. The type of the output pixels is the union of the input types.
#
# Args:
#   image1: The image from which the left operand bands are taken.
#   image2: The image from which the right operand bands are taken.
signatures.append({'args': [{'description': 'The image from which the left operand bands are taken.', 'name': 'image1', 'type': 'Image'}, {'description': 'The image from which the right operand bands are taken.', 'name': 'image2', 'type': 'Image'}], 'description': "Divides the first value by the second, returning 0 for division by 0 for each matched pair of bands in image1 and image2. If either image1 or image2 has only 1 band, then it is used against all the bands in the other image. If the images have the same number of bands, but not the same names, they're used pairwise in the natural order. The output bands are named for the longer of the two inputs, or if they're equal in length, in image1's order. The type of the output pixels is the union of the input types.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.divide'})
# Image.double
# Casts the input value to a 64-bit float.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Casts the input value to a 64-bit float.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.double'})
# Image.entropy
# Computes the windowed entropy for each band using the specified kernel
# centered on each input pixel.
#
# Args:
#   image: The image for which to compute the entropy.
#   kernel: A kernel specifying the window in which to compute.
signatures.append({'args': [{'description': 'The image for which to compute the entropy.', 'name': 'image', 'type': 'Image'}, {'description': 'A kernel specifying the window in which to compute.', 'name': 'kernel', 'type': 'Kernel'}], 'description': 'Computes the windowed entropy for each band using the specified kernel centered on each input pixel.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.entropy'})
# Image.eq
# Returns 1 iff the first value is equal to the second for each matched pair
# of bands in image1 and image2. If either image1 or image2 has only 1 band,
# then it is used against all the bands in the other image. If the images
# have the same number of bands, but not the same names, they're used
# pairwise in the natural order. The output bands are named for the longer of
# the two inputs, or if they're equal in length, in image1's order. The type
# of the output pixels is boolean.
#
# Args:
#   image1: The image from which the left operand bands are taken.
#   image2: The image from which the right operand bands are taken.
signatures.append({'args': [{'description': 'The image from which the left operand bands are taken.', 'name': 'image1', 'type': 'Image'}, {'description': 'The image from which the right operand bands are taken.', 'name': 'image2', 'type': 'Image'}], 'description': "Returns 1 iff the first value is equal to the second for each matched pair of bands in image1 and image2. If either image1 or image2 has only 1 band, then it is used against all the bands in the other image. If the images have the same number of bands, but not the same names, they're used pairwise in the natural order. The output bands are named for the longer of the two inputs, or if they're equal in length, in image1's order. The type of the output pixels is boolean.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.eq'})
# Image.erf
# Computes the error function of the input.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Computes the error function of the input.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.erf'})
# Image.erfInv
# Computes the inverse error function of the input.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Computes the inverse error function of the input.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.erfInv'})
# Image.erfc
# Computes the complementary error function of the input.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Computes the complementary error function of the input.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.erfc'})
# Image.erfcInv
# Computes the inverse complementary error function of the input.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Computes the inverse complementary error function of the input.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.erfcInv'})
# Image.exp
# Computes the Euler's number e raised to the power of the input.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': "Computes the Euler's number e raised to the power of the input.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.exp'})
# Image.fastDistanceTransform
# Returns the distance, as determined by the specified distance metric, to
# the nearest non-zero valued pixel in the input.  The output contains values
# for all pixels within the given neighborhood size, regardless of the
# input's mask.  Note: the default distance metric returns squared distance.
#
# Args:
#   image: The input image.
#   neighborhood: Neighborhood size in pixels.
#   units: The units of the neighborhood, currently only 'pixels'
#       are supported.
#   metric: Distance metric to use: options are
#       'squared_euclidean', 'manhattan' or 'chebyshev'.
signatures.append({'args': [{'description': 'The input image.', 'name': 'image', 'type': 'Image'}, {'default': 256, 'description': 'Neighborhood size in pixels.', 'name': 'neighborhood', 'optional': True, 'type': 'Integer'}, {'default': 'pixels', 'description': "The units of the neighborhood, currently only 'pixels' are supported.", 'name': 'units', 'optional': True, 'type': 'String'}, {'default': 'squared_euclidean', 'description': "Distance metric to use: options are 'squared_euclidean', 'manhattan' or 'chebyshev'.", 'name': 'metric', 'optional': True, 'type': 'String'}], 'description': "Returns the distance, as determined by the specified distance metric, to the nearest non-zero valued pixel in the input.  The output contains values for all pixels within the given neighborhood size, regardless of the input's mask.  Note: the default distance metric returns squared distance.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.fastDistanceTransform'})
# Image.fastGaussianBlur
# Applies an approximate Gaussian blurring operation to each band of an
# image.  This algorithm computes the convolution of the image with a
# Gaussian smoothing kernel with the given standard deviation. Equivalently,
# this algorithm applies a spatial low-pass filter with a cutoff at the given
# spatial wavelength.  The implementation uses an efficient, approximate
# method for large kernels: it will evaluate the input data at a reduced
# resolution, apply a smaller kernel to that data, and then bicubically
# resample the result.  NOTE: The kernel size is specified in meters, and
# this is converted to a kernel size in pixels based on the particular map
# projection in which this operation is being applied. As a result, the
# effective kernel size may vary if you apply this operation in a region away
# from the map projection's region of true scale. For example, if you are
# operating in a Mercator projection then the kernel size will be accurate
# near the equator but will become increasingly inaccurate at high latitudes.
#
# Args:
#   image: The input image.
#   sigma: The standard deviation of the Gaussian kernel, in meters.
#       Equivalently, the spatial wavelength of the low-pass filter.
signatures.append({'args': [{'description': 'The input image.', 'name': 'image', 'type': 'Image'}, {'description': 'The standard deviation of the Gaussian kernel, in meters. Equivalently, the spatial wavelength of the low-pass filter.', 'name': 'sigma', 'type': 'Float'}], 'description': "Applies an approximate Gaussian blurring operation to each band of an image.\n\nThis algorithm computes the convolution of the image with a Gaussian smoothing kernel with the given standard deviation. Equivalently, this algorithm applies a spatial low-pass filter with a cutoff at the given spatial wavelength.\n\nThe implementation uses an efficient, approximate method for large kernels: it will evaluate the input data at a reduced resolution, apply a smaller kernel to that data, and then bicubically resample the result.\n\nNOTE: The kernel size is specified in meters, and this is converted to a kernel size in pixels based on the particular map projection in which this operation is being applied. As a result, the effective kernel size may vary if you apply this operation in a region away from the map projection's region of true scale. For example, if you are operating in a Mercator projection then the kernel size will be accurate near the equator but will become increasingly inaccurate at high latitudes.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.fastGaussianBlur'})
# Image.first
# Selects the value of the first value for each matched pair of bands in
# image1 and image2. If either image1 or image2 has only 1 band, then it is
# used against all the bands in the other image. If the images have the same
# number of bands, but not the same names, they're used pairwise in the
# natural order. The output bands are named for the longer of the two inputs,
# or if they're equal in length, in image1's order. The type of the output
# pixels is the union of the input types.
#
# Args:
#   image1: The image from which the left operand bands are taken.
#   image2: The image from which the right operand bands are taken.
signatures.append({'args': [{'description': 'The image from which the left operand bands are taken.', 'name': 'image1', 'type': 'Image'}, {'description': 'The image from which the right operand bands are taken.', 'name': 'image2', 'type': 'Image'}], 'description': "Selects the value of the first value for each matched pair of bands in image1 and image2. If either image1 or image2 has only 1 band, then it is used against all the bands in the other image. If the images have the same number of bands, but not the same names, they're used pairwise in the natural order. The output bands are named for the longer of the two inputs, or if they're equal in length, in image1's order. The type of the output pixels is the union of the input types.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.first'})
# Image.firstNonZero
# Selects the first value if it is non-zero, and the second value otherwise
# for each matched pair of bands in image1 and image2. If either image1 or
# image2 has only 1 band, then it is used against all the bands in the other
# image. If the images have the same number of bands, but not the same names,
# they're used pairwise in the natural order. The output bands are named for
# the longer of the two inputs, or if they're equal in length, in image1's
# order. The type of the output pixels is the union of the input types.
#
# Args:
#   image1: The image from which the left operand bands are taken.
#   image2: The image from which the right operand bands are taken.
signatures.append({'args': [{'description': 'The image from which the left operand bands are taken.', 'name': 'image1', 'type': 'Image'}, {'description': 'The image from which the right operand bands are taken.', 'name': 'image2', 'type': 'Image'}], 'description': "Selects the first value if it is non-zero, and the second value otherwise for each matched pair of bands in image1 and image2. If either image1 or image2 has only 1 band, then it is used against all the bands in the other image. If the images have the same number of bands, but not the same names, they're used pairwise in the natural order. The output bands are named for the longer of the two inputs, or if they're equal in length, in image1's order. The type of the output pixels is the union of the input types.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.firstNonZero'})
# Image.first_nonzero
# Selects the first value if it is non-zero, and the second value otherwise
# for each matched pair of bands in image1 and image2. If either image1 or
# image2 has only 1 band, then it is used against all the bands in the other
# image. If the images have the same number of bands, but not the same names,
# they're used pairwise in the natural order. The output bands are named for
# the longer of the two inputs, or if they're equal in length, in image1's
# order. The type of the output pixels is the union of the input types.
#
# Args:
#   image1: The image from which the left operand bands are taken.
#   image2: The image from which the right operand bands are taken.
signatures.append({'args': [{'description': 'The image from which the left operand bands are taken.', 'name': 'image1', 'type': 'Image'}, {'description': 'The image from which the right operand bands are taken.', 'name': 'image2', 'type': 'Image'}], 'description': "Selects the first value if it is non-zero, and the second value otherwise for each matched pair of bands in image1 and image2. If either image1 or image2 has only 1 band, then it is used against all the bands in the other image. If the images have the same number of bands, but not the same names, they're used pairwise in the natural order. The output bands are named for the longer of the two inputs, or if they're equal in length, in image1's order. The type of the output pixels is the union of the input types.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.first_nonzero'})
# Image.float
# Casts the input value to a 32-bit float.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Casts the input value to a 32-bit float.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.float'})
# Image.floor
# Computes the largest integer less than or equal to the input.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Computes the largest integer less than or equal to the input.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.floor'})
# Image.gamma
# Computes the gamma function of the input.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Computes the gamma function of the input.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.gamma'})
# Image.gammainc
# Calculates the regularized lower incomplete Gamma function (&gamma;(x,a)
# for each matched pair of bands in image1 and image2. If either image1 or
# image2 has only 1 band, then it is used against all the bands in the other
# image. If the images have the same number of bands, but not the same names,
# they're used pairwise in the natural order. The output bands are named for
# the longer of the two inputs, or if they're equal in length, in image1's
# order. The type of the output pixels is float.
#
# Args:
#   image1: The image from which the left operand bands are taken.
#   image2: The image from which the right operand bands are taken.
signatures.append({'args': [{'description': 'The image from which the left operand bands are taken.', 'name': 'image1', 'type': 'Image'}, {'description': 'The image from which the right operand bands are taken.', 'name': 'image2', 'type': 'Image'}], 'description': "Calculates the regularized lower incomplete Gamma function (&gamma;(x,a) for each matched pair of bands in image1 and image2. If either image1 or image2 has only 1 band, then it is used against all the bands in the other image. If the images have the same number of bands, but not the same names, they're used pairwise in the natural order. The output bands are named for the longer of the two inputs, or if they're equal in length, in image1's order. The type of the output pixels is float.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.gammainc'})
# Image.geometry
# Returns the geometry of a given feature in a given projection.
#
# Args:
#   feature: The feature from which the geometry is taken.
#   maxError: The maximum amount of error tolerated when
#       performing any necessary reprojection.
#   proj: If specified, the geometry will be in this projection. If
#       unspecified, the geometry will be in its default projection.
#   geodesics: If true, the geometry will have geodesic edges.
#       If false, it will have edges as straight lines in the
#       specified projection. If null, the edge interpretation
#       will be the same as the original geometry. This argument
#       is ignored if proj is not specified.
signatures.append({'args': [{'description': 'The feature from which the geometry is taken.', 'name': 'feature', 'type': 'Element'}, {'default': None, 'description': 'The maximum amount of error tolerated when performing any necessary reprojection.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}, {'default': None, 'description': 'If specified, the geometry will be in this projection. If unspecified, the geometry will be in its default projection.', 'name': 'proj', 'optional': True, 'type': 'Projection'}, {'default': None, 'description': 'If true, the geometry will have geodesic edges. If false, it will have edges as straight lines in the specified projection. If null, the edge interpretation will be the same as the original geometry. This argument is ignored if proj is not specified.', 'name': 'geodesics', 'optional': True, 'type': 'Boolean'}], 'description': 'Returns the geometry of a given feature in a given projection.', 'returns': 'Geometry', 'type': 'Algorithm', 'hidden': False, 'deprecated': 'Use Element.geometry()', 'name': 'Image.geometry'})
# Image.glcmTexture
# Computes texture metrics from the Gray Level Co-occurrence Matrix around
# each pixel of every band.
#
# Args:
#   image: The image for which to compute texture metrics.
#   size: The size of the neighborhood to include in each GLCM.
#   kernel: A kernel specifying the x and y offsets over which to
#       compute the GLCMs.  A GLCM is computed for each pixel in
#       the kernel that is non-zero, except the center pixel and as
#       long as a GLCM hasn't already been computed for the same
#       direction and distance.  For example, if either or both of
#       the east and west pixels are set, only 1 (horizontal) GLCM
#       is computed.  Kernels are scanned from left to right and
#       top to bottom.  The default is a 3x3 square, resulting in 4
#       GLCMs with the offsets (-1, -1), (0, -1), (1, -1) and (-1,
#       0).
#   average: If true, the directional bands for each metric are
#       averaged.
signatures.append({'args': [{'description': 'The image for which to compute texture metrics.', 'name': 'image', 'type': 'Image'}, {'default': 1, 'description': 'The size of the neighborhood to include in each GLCM.', 'name': 'size', 'optional': True, 'type': 'Integer'}, {'default': None, 'description': "A kernel specifying the x and y offsets over which to compute the GLCMs.  A GLCM is computed for each pixel in the kernel that is non-zero, except the center pixel and as long as a GLCM hasn't already been computed for the same direction and distance.  For example, if either or both of the east and west pixels are set, only 1 (horizontal) GLCM is computed.  Kernels are scanned from left to right and top to bottom.  The default is a 3x3 square, resulting in 4 GLCMs with the offsets (-1, -1), (0, -1), (1, -1) and (-1, 0).", 'name': 'kernel', 'optional': True, 'type': 'Kernel'}, {'default': True, 'description': 'If true, the directional bands for each metric are averaged.', 'name': 'average', 'optional': True, 'type': 'Boolean'}], 'description': 'Computes texture metrics from the Gray Level Co-occurrence Matrix around each pixel of every band.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.glcmTexture'})
# Image.gradient
# Calculates the x and y gradient.
#
# Args:
#   input: The input image.
signatures.append({'args': [{'description': 'The input image.', 'name': 'input', 'type': 'Image'}], 'description': 'Calculates the x and y gradient.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.gradient'})
# Image.gt
# Returns 1 iff the first value is greater than the second for each matched
# pair of bands in image1 and image2. If either image1 or image2 has only 1
# band, then it is used against all the bands in the other image. If the
# images have the same number of bands, but not the same names, they're used
# pairwise in the natural order. The output bands are named for the longer of
# the two inputs, or if they're equal in length, in image1's order. The type
# of the output pixels is boolean.
#
# Args:
#   image1: The image from which the left operand bands are taken.
#   image2: The image from which the right operand bands are taken.
signatures.append({'args': [{'description': 'The image from which the left operand bands are taken.', 'name': 'image1', 'type': 'Image'}, {'description': 'The image from which the right operand bands are taken.', 'name': 'image2', 'type': 'Image'}], 'description': "Returns 1 iff the first value is greater than the second for each matched pair of bands in image1 and image2. If either image1 or image2 has only 1 band, then it is used against all the bands in the other image. If the images have the same number of bands, but not the same names, they're used pairwise in the natural order. The output bands are named for the longer of the two inputs, or if they're equal in length, in image1's order. The type of the output pixels is boolean.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.gt'})
# Image.gte
# Returns 1 iff the first value is greater than or equal to the second for
# each matched pair of bands in image1 and image2. If either image1 or image2
# has only 1 band, then it is used against all the bands in the other image.
# If the images have the same number of bands, but not the same names,
# they're used pairwise in the natural order. The output bands are named for
# the longer of the two inputs, or if they're equal in length, in image1's
# order. The type of the output pixels is boolean.
#
# Args:
#   image1: The image from which the left operand bands are taken.
#   image2: The image from which the right operand bands are taken.
signatures.append({'args': [{'description': 'The image from which the left operand bands are taken.', 'name': 'image1', 'type': 'Image'}, {'description': 'The image from which the right operand bands are taken.', 'name': 'image2', 'type': 'Image'}], 'description': "Returns 1 iff the first value is greater than or equal to the second for each matched pair of bands in image1 and image2. If either image1 or image2 has only 1 band, then it is used against all the bands in the other image. If the images have the same number of bands, but not the same names, they're used pairwise in the natural order. The output bands are named for the longer of the two inputs, or if they're equal in length, in image1's order. The type of the output pixels is boolean.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.gte'})
# Image.hsvToRgb
# Transforms the image from the HSV color space to the RGB color space.
# Produces three bands: red, green and blue, all floating point values in the
# range [0, 1].
#
# Args:
#   image: The image to transform.
signatures.append({'args': [{'description': 'The image to transform.', 'name': 'image', 'type': 'Image'}], 'description': 'Transforms the image from the HSV color space to the RGB color space. Produces three bands: red, green and blue, all floating point values in the range [0, 1].', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.hsvToRgb'})
# Image.hypot
# Calculates the magnitude of the 2D vector [x, y] for each matched pair of
# bands in image1 and image2. If either image1 or image2 has only 1 band,
# then it is used against all the bands in the other image. If the images
# have the same number of bands, but not the same names, they're used
# pairwise in the natural order. The output bands are named for the longer of
# the two inputs, or if they're equal in length, in image1's order. The type
# of the output pixels is float.
#
# Args:
#   image1: The image from which the left operand bands are taken.
#   image2: The image from which the right operand bands are taken.
signatures.append({'args': [{'description': 'The image from which the left operand bands are taken.', 'name': 'image1', 'type': 'Image'}, {'description': 'The image from which the right operand bands are taken.', 'name': 'image2', 'type': 'Image'}], 'description': "Calculates the magnitude of the 2D vector [x, y] for each matched pair of bands in image1 and image2. If either image1 or image2 has only 1 band, then it is used against all the bands in the other image. If the images have the same number of bands, but not the same names, they're used pairwise in the natural order. The output bands are named for the longer of the two inputs, or if they're equal in length, in image1's order. The type of the output pixels is float.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.hypot'})
# Image.id
# Returns the ID of a given element within a collection. Objects outside
# collections are not guaranteed to have IDs.
#
# Args:
#   element: The element from which the ID is taken.
signatures.append({'args': [{'description': 'The element from which the ID is taken.', 'name': 'element', 'type': 'Element'}], 'description': 'Returns the ID of a given element within a collection. Objects outside collections are not guaranteed to have IDs.', 'returns': 'String', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.id'})
# Image.int
# Casts the input value to a signed 32-bit integer.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Casts the input value to a signed 32-bit integer.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.int'})
# Image.int16
# Casts the input value to a signed 16-bit integer.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Casts the input value to a signed 16-bit integer.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.int16'})
# Image.int32
# Casts the input value to a signed 32-bit integer.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Casts the input value to a signed 32-bit integer.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.int32'})
# Image.int64
# Casts the input value to a signed 64-bit integer.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Casts the input value to a signed 64-bit integer.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.int64'})
# Image.int8
# Casts the input value to a signed 8-bit integer.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Casts the input value to a signed 8-bit integer.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.int8'})
# Image.interpolate
# Interpolates each point in the first band of the input image into the
# piecewise-linear function specified by the x and y arrays.  The x values
# must be strictly increasing.  If an input point is less than the first or
# greater than the last x value, then the output is specified by the
# "behavior" argument: "extrapolate" specifies the output value is
# extrapolated from the two nearest points, "clamp" specifies the output
# value is taken from the nearest point, "input"  specifies the output value
# is copied from the input and "mask" specifies the output value is masked.
#
# Args:
#   image: The image to which the interpolation is applied.
#   x: The x axis (input) values in the piecewise function.
#   y: The y axis (output) values in the piecewise function.
#   behavior: The behavior for points that are outside of the
#       range of the supplied function.  Options are:
#       'extrapolate', 'clamp', 'mask' or 'input'.
signatures.append({'args': [{'description': 'The image to which the interpolation is applied.', 'name': 'image', 'type': 'Image'}, {'description': 'The x axis (input) values in the piecewise function.', 'name': 'x', 'type': 'List'}, {'description': 'The y axis (output) values in the piecewise function.', 'name': 'y', 'type': 'List'}, {'default': 'extrapolate', 'description': "The behavior for points that are outside of the range of the supplied function.  Options are: 'extrapolate', 'clamp', 'mask' or 'input'.", 'name': 'behavior', 'optional': True, 'type': 'String'}], 'description': 'Interpolates each point in the first band of the input image into the piecewise-linear function specified by the x and y arrays.  The x values must be strictly increasing.  If an input point is less than the first or greater than the last x value, then the output is specified by the "behavior" argument: "extrapolate" specifies the output value is extrapolated from the two nearest points, "clamp" specifies the output value is taken from the nearest point, "input"  specifies the output value is copied from the input and "mask" specifies the output value is masked.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.interpolate'})
# Image.lanczos
# Computes the Lanczos approximation of the input.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Computes the Lanczos approximation of the input.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.lanczos'})
# Image.leftShift
# Calculates the left shift of v1 by v2 bits for each matched pair of bands
# in image1 and image2. If either image1 or image2 has only 1 band, then it
# is used against all the bands in the other image. If the images have the
# same number of bands, but not the same names, they're used pairwise in the
# natural order. The output bands are named for the longer of the two inputs,
# or if they're equal in length, in image1's order. The type of the output
# pixels is the union of the input types.
#
# Args:
#   image1: The image from which the left operand bands are taken.
#   image2: The image from which the right operand bands are taken.
signatures.append({'args': [{'description': 'The image from which the left operand bands are taken.', 'name': 'image1', 'type': 'Image'}, {'description': 'The image from which the right operand bands are taken.', 'name': 'image2', 'type': 'Image'}], 'description': "Calculates the left shift of v1 by v2 bits for each matched pair of bands in image1 and image2. If either image1 or image2 has only 1 band, then it is used against all the bands in the other image. If the images have the same number of bands, but not the same names, they're used pairwise in the natural order. The output bands are named for the longer of the two inputs, or if they're equal in length, in image1's order. The type of the output pixels is the union of the input types.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.leftShift'})
# Image.left_shift
# Calculates the left shift of v1 by v2 bits for each matched pair of bands
# in image1 and image2. If either image1 or image2 has only 1 band, then it
# is used against all the bands in the other image. If the images have the
# same number of bands, but not the same names, they're used pairwise in the
# natural order. The output bands are named for the longer of the two inputs,
# or if they're equal in length, in image1's order. The type of the output
# pixels is the union of the input types.
#
# Args:
#   image1: The image from which the left operand bands are taken.
#   image2: The image from which the right operand bands are taken.
signatures.append({'args': [{'description': 'The image from which the left operand bands are taken.', 'name': 'image1', 'type': 'Image'}, {'description': 'The image from which the right operand bands are taken.', 'name': 'image2', 'type': 'Image'}], 'description': "Calculates the left shift of v1 by v2 bits for each matched pair of bands in image1 and image2. If either image1 or image2 has only 1 band, then it is used against all the bands in the other image. If the images have the same number of bands, but not the same names, they're used pairwise in the natural order. The output bands are named for the longer of the two inputs, or if they're equal in length, in image1's order. The type of the output pixels is the union of the input types.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.left_shift'})
# Image.load
# Returns the image given its ID.
#
# Args:
#   id: The asset ID of the image.
#   version: The version of the asset. -1 signifies the latest
#       version.
signatures.append({'args': [{'description': 'The asset ID of the image.', 'name': 'id', 'type': 'String'}, {'default': -1, 'description': 'The version of the asset. -1 signifies the latest version.', 'name': 'version', 'optional': True, 'type': 'Long'}], 'description': 'Returns the image given its ID.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.load'})
# Image.log
# Computes the natural logarithm of the input.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Computes the natural logarithm of the input.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.log'})
# Image.log10
# Computes the base-10 logarithm of the input.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Computes the base-10 logarithm of the input.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.log10'})
# Image.long
# Casts the input value to a signed 64-bit integer.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Casts the input value to a signed 64-bit integer.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.long'})
# Image.lt
# Returns 1 iff the first value is less than the second for each matched pair
# of bands in image1 and image2. If either image1 or image2 has only 1 band,
# then it is used against all the bands in the other image. If the images
# have the same number of bands, but not the same names, they're used
# pairwise in the natural order. The output bands are named for the longer of
# the two inputs, or if they're equal in length, in image1's order. The type
# of the output pixels is boolean.
#
# Args:
#   image1: The image from which the left operand bands are taken.
#   image2: The image from which the right operand bands are taken.
signatures.append({'args': [{'description': 'The image from which the left operand bands are taken.', 'name': 'image1', 'type': 'Image'}, {'description': 'The image from which the right operand bands are taken.', 'name': 'image2', 'type': 'Image'}], 'description': "Returns 1 iff the first value is less than the second for each matched pair of bands in image1 and image2. If either image1 or image2 has only 1 band, then it is used against all the bands in the other image. If the images have the same number of bands, but not the same names, they're used pairwise in the natural order. The output bands are named for the longer of the two inputs, or if they're equal in length, in image1's order. The type of the output pixels is boolean.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.lt'})
# Image.lte
# Returns 1 iff the first value is less than or equal to the second for each
# matched pair of bands in image1 and image2. If either image1 or image2 has
# only 1 band, then it is used against all the bands in the other image. If
# the images have the same number of bands, but not the same names, they're
# used pairwise in the natural order. The output bands are named for the
# longer of the two inputs, or if they're equal in length, in image1's order.
# The type of the output pixels is boolean.
#
# Args:
#   image1: The image from which the left operand bands are taken.
#   image2: The image from which the right operand bands are taken.
signatures.append({'args': [{'description': 'The image from which the left operand bands are taken.', 'name': 'image1', 'type': 'Image'}, {'description': 'The image from which the right operand bands are taken.', 'name': 'image2', 'type': 'Image'}], 'description': "Returns 1 iff the first value is less than or equal to the second for each matched pair of bands in image1 and image2. If either image1 or image2 has only 1 band, then it is used against all the bands in the other image. If the images have the same number of bands, but not the same names, they're used pairwise in the natural order. The output bands are named for the longer of the two inputs, or if they're equal in length, in image1's order. The type of the output pixels is boolean.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.lte'})
# Image.mask
# Gets or sets an image's mask. The output image retains the metadata and
# footprint of the input image. Pixels where the mask changes from zero to
# another value will be filled with zeros, or the values closest to zero
# within the range of the pixel type. Note: the version that sets a mask will
# be deprecated. To set a mask from an image on previously unmasked pixels,
# use Image.updateMask. To unmask previously masked pixels, use Image.unmask.
#
# Args:
#   image: The input image.
#   mask: The mask image. If specified, the input image is copied to
#       the output but given the mask by the values of this image. If
#       this is a single band, it is used for all bands in the input
#       image. If not specified, returns an image created from the
#       mask of the input image, scaled to the range [0:1] (invalid =
#       0, valid = 1.0).
signatures.append({'args': [{'description': 'The input image.', 'name': 'image', 'type': 'Image'}, {'default': None, 'description': 'The mask image. If specified, the input image is copied to the output but given the mask by the values of this image. If this is a single band, it is used for all bands in the input image. If not specified, returns an image created from the mask of the input image, scaled to the range [0:1] (invalid = 0, valid = 1.0).', 'name': 'mask', 'optional': True, 'type': 'Image'}], 'description': "Gets or sets an image's mask. The output image retains the metadata and footprint of the input image. Pixels where the mask changes from zero to another value will be filled with zeros, or the values closest to zero within the range of the pixel type.\nNote: the version that sets a mask will be deprecated. To set a mask from an image on previously unmasked pixels, use Image.updateMask. To unmask previously masked pixels, use Image.unmask.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.mask'})
# Image.matrixCholeskyDecomposition
# Calculates the Cholesky decomposition of a matrix. The Cholesky
# decomposition is a decomposition into the form L*L' where L is a lower
# triangular matrix. The input must be a symmetric positive-definite matrix.
# Returns an image with 1 band named 'L'.
#
# Args:
#   image: Image of 2-D matrices to be decomposed.
signatures.append({'args': [{'description': 'Image of 2-D matrices to be decomposed.', 'name': 'image', 'type': 'Image'}], 'description': "Calculates the Cholesky decomposition of a matrix. The Cholesky decomposition is a decomposition into the form L*L' where L is a lower triangular matrix. The input must be a symmetric positive-definite matrix. Returns an image with 1 band named 'L'.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.matrixCholeskyDecomposition'})
# Image.matrixDeterminant
# Computes the determinant of the matrix.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Computes the determinant of the matrix.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.matrixDeterminant'})
# Image.matrixDiagonal
# Computes the diagonal of the matrix in a single column.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Computes the diagonal of the matrix in a single column.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.matrixDiagonal'})
# Image.matrixFnorm
# Computes the Frobenius norm of the matrix.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Computes the Frobenius norm of the matrix.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.matrixFnorm'})
# Image.matrixIdentity
# Creates an image where each pixel is a 2D identity matrix of the given
# size.
#
# Args:
#   size: The length of each axis.
signatures.append({'args': [{'description': 'The length of each axis.', 'name': 'size', 'type': 'Integer'}], 'description': 'Creates an image where each pixel is a 2D identity matrix of the given size.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.matrixIdentity'})
# Image.matrixInverse
# Computes the inverse of the matrix.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Computes the inverse of the matrix.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.matrixInverse'})
# Image.matrixLUDecomposition
# Calculates the LU matrix decomposition such that P×input=L×U, where L is
# lower triangular (with unit diagonal terms), U is upper triangular and P is
# a partial pivot permutation matrix. The input matrix must be square.
# Returns an image with bands named 'L', 'U' and 'P'.
#
# Args:
#   image: Image of 2-D matrices to be decomposed.
signatures.append({'args': [{'description': 'Image of 2-D matrices to be decomposed.', 'name': 'image', 'type': 'Image'}], 'description': "Calculates the LU matrix decomposition such that P×input=L×U, where L is lower triangular (with unit diagonal terms), U is upper triangular and P is a partial pivot permutation matrix. The input matrix must be square. Returns an image with bands named 'L', 'U' and 'P'.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.matrixLUDecomposition'})
# Image.matrixMultiply
# Returns the matrix multiplication A*B for each matched pair of bands in
# image1 and image2. If either image1 or image2 has only 1 band, then it is
# used against all the bands in the other image. If the images have the same
# number of bands, but not the same names, they're used pairwise in the
# natural order. The output bands are named for the longer of the two inputs,
# or if they're equal in length, in image1's order. The type of the output
# pixels is the union of the input types.
#
# Args:
#   image1: The image from which the left operand bands are taken.
#   image2: The image from which the right operand bands are taken.
signatures.append({'args': [{'description': 'The image from which the left operand bands are taken.', 'name': 'image1', 'type': 'Image'}, {'description': 'The image from which the right operand bands are taken.', 'name': 'image2', 'type': 'Image'}], 'description': "Returns the matrix multiplication A*B for each matched pair of bands in image1 and image2. If either image1 or image2 has only 1 band, then it is used against all the bands in the other image. If the images have the same number of bands, but not the same names, they're used pairwise in the natural order. The output bands are named for the longer of the two inputs, or if they're equal in length, in image1's order. The type of the output pixels is the union of the input types.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.matrixMultiply'})
# Image.matrixPseudoInverse
# Computes the Moore-Penrose pseudoinverse of the matrix.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Computes the Moore-Penrose pseudoinverse of the matrix.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.matrixPseudoInverse'})
# Image.matrixQRDecomposition
# Calculates the QR-decomposition of a matrix into two matrices Q and R such
# that input = QR, where Q is orthogonal, and R is upper triangular. Returns
# an image with bands named 'Q' and 'R'.
#
# Args:
#   image: Image of 2-D matrices to be decomposed.
signatures.append({'args': [{'description': 'Image of 2-D matrices to be decomposed.', 'name': 'image', 'type': 'Image'}], 'description': "Calculates the QR-decomposition of a matrix into two matrices Q and R such that input = QR, where Q is orthogonal, and R is upper triangular. Returns an image with bands named 'Q' and 'R'.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.matrixQRDecomposition'})
# Image.matrixSingularValueDecomposition
# Calculates the Singular Value Decomposition of the input matrix into
# U×S×V', such that U and V are orthogonal and S is diagonal. Returns an
# image with bands named 'U', 'S' and 'V'.
#
# Args:
#   image: Image of 2-D matrices to be decomposed.
signatures.append({'args': [{'description': 'Image of 2-D matrices to be decomposed.', 'name': 'image', 'type': 'Image'}], 'description': "Calculates the Singular Value Decomposition of the input matrix into U×S×V', such that U and V are orthogonal and S is diagonal. Returns an image with bands named 'U', 'S' and 'V'.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.matrixSingularValueDecomposition'})
# Image.matrixSolve
# Solves for x in the matrix equation A*x=B, finding a least-squares solution
# if A is overdetermined for each matched pair of bands in image1 and image2.
# If either image1 or image2 has only 1 band, then it is used against all the
# bands in the other image. If the images have the same number of bands, but
# not the same names, they're used pairwise in the natural order. The output
# bands are named for the longer of the two inputs, or if they're equal in
# length, in image1's order. The type of the output pixels is the union of
# the input types.
#
# Args:
#   image1: The image from which the left operand bands are taken.
#   image2: The image from which the right operand bands are taken.
signatures.append({'args': [{'description': 'The image from which the left operand bands are taken.', 'name': 'image1', 'type': 'Image'}, {'description': 'The image from which the right operand bands are taken.', 'name': 'image2', 'type': 'Image'}], 'description': "Solves for x in the matrix equation A*x=B, finding a least-squares solution if A is overdetermined for each matched pair of bands in image1 and image2. If either image1 or image2 has only 1 band, then it is used against all the bands in the other image. If the images have the same number of bands, but not the same names, they're used pairwise in the natural order. The output bands are named for the longer of the two inputs, or if they're equal in length, in image1's order. The type of the output pixels is the union of the input types.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.matrixSolve'})
# Image.matrixToDiag
# Computes a square diagonal matrix from a single column matrix.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Computes a square diagonal matrix from a single column matrix.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.matrixToDiag'})
# Image.matrixTrace
# Computes the trace of the matrix.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Computes the trace of the matrix.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.matrixTrace'})
# Image.matrixTranspose
# Transposes two dimensions of each array pixel.
#
# Args:
#   input: Input image.
#   axis1: First axis to swap.
#   axis2: Second axis to swap.
signatures.append({'args': [{'description': 'Input image.', 'name': 'input', 'type': 'Image'}, {'default': 0, 'description': 'First axis to swap.', 'name': 'axis1', 'optional': True, 'type': 'Integer'}, {'default': 1, 'description': 'Second axis to swap.', 'name': 'axis2', 'optional': True, 'type': 'Integer'}], 'description': 'Transposes two dimensions of each array pixel.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.matrixTranspose'})
# Image.max
# Selects the maximum of the first and second values for each matched pair of
# bands in image1 and image2. If either image1 or image2 has only 1 band,
# then it is used against all the bands in the other image. If the images
# have the same number of bands, but not the same names, they're used
# pairwise in the natural order. The output bands are named for the longer of
# the two inputs, or if they're equal in length, in image1's order. The type
# of the output pixels is the union of the input types.
#
# Args:
#   image1: The image from which the left operand bands are taken.
#   image2: The image from which the right operand bands are taken.
signatures.append({'args': [{'description': 'The image from which the left operand bands are taken.', 'name': 'image1', 'type': 'Image'}, {'description': 'The image from which the right operand bands are taken.', 'name': 'image2', 'type': 'Image'}], 'description': "Selects the maximum of the first and second values for each matched pair of bands in image1 and image2. If either image1 or image2 has only 1 band, then it is used against all the bands in the other image. If the images have the same number of bands, but not the same names, they're used pairwise in the natural order. The output bands are named for the longer of the two inputs, or if they're equal in length, in image1's order. The type of the output pixels is the union of the input types.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.max'})
# Image.medialAxis
# Computes the discrete medial axis of the zero valued pixels of the first
# band of the input.  Outputs 4 bands:  medial - the medial axis points,
# scaled by the distance.  coverage - the number of points supporting each
# medial axis point.  xlabel - the horizontal distance to the power point for
# each pixel.  ylabel - the vertical distance to the power point for each
# pixel.
#
# Args:
#   image: The input image.
#   neighborhood: Neighborhood size in pixels.
#   units: The units of the neighborhood, currently only 'pixels'
#       are supported.
signatures.append({'args': [{'description': 'The input image.', 'name': 'image', 'type': 'Image'}, {'default': 256, 'description': 'Neighborhood size in pixels.', 'name': 'neighborhood', 'optional': True, 'type': 'Integer'}, {'default': 'pixels', 'description': "The units of the neighborhood, currently only 'pixels' are supported.", 'name': 'units', 'optional': True, 'type': 'String'}], 'description': 'Computes the discrete medial axis of the zero valued pixels of the first band of the input.  Outputs 4 bands:\n medial - the medial axis points, scaled by the distance.\n coverage - the number of points supporting each medial axis point.\n xlabel - the horizontal distance to the power point for each pixel.\n ylabel - the vertical distance to the power point for each pixel.\n', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.medialAxis'})
# Image.metadata
# Generates a constant image of type double from a metadata property.
#
# Args:
#   image: The image from which to get the metadata
#   property: The property from which to take the value.
#   name: The name for the output band.  If unspecified, it will be
#       the same as the property name.
signatures.append({'args': [{'description': 'The image from which to get the metadata', 'name': 'image', 'type': 'Image'}, {'description': 'The property from which to take the value.', 'name': 'property', 'type': 'String'}, {'default': None, 'description': 'The name for the output band.  If unspecified, it will be the same as the property name.', 'name': 'name', 'optional': True, 'type': 'String'}], 'description': 'Generates a constant image of type double from a metadata property.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.metadata'})
# Image.min
# Selects the minimum of the first and second values for each matched pair of
# bands in image1 and image2. If either image1 or image2 has only 1 band,
# then it is used against all the bands in the other image. If the images
# have the same number of bands, but not the same names, they're used
# pairwise in the natural order. The output bands are named for the longer of
# the two inputs, or if they're equal in length, in image1's order. The type
# of the output pixels is the union of the input types.
#
# Args:
#   image1: The image from which the left operand bands are taken.
#   image2: The image from which the right operand bands are taken.
signatures.append({'args': [{'description': 'The image from which the left operand bands are taken.', 'name': 'image1', 'type': 'Image'}, {'description': 'The image from which the right operand bands are taken.', 'name': 'image2', 'type': 'Image'}], 'description': "Selects the minimum of the first and second values for each matched pair of bands in image1 and image2. If either image1 or image2 has only 1 band, then it is used against all the bands in the other image. If the images have the same number of bands, but not the same names, they're used pairwise in the natural order. The output bands are named for the longer of the two inputs, or if they're equal in length, in image1's order. The type of the output pixels is the union of the input types.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.min'})
# Image.mod
# Calculates the remainder of the first value divided by the second for each
# matched pair of bands in image1 and image2. If either image1 or image2 has
# only 1 band, then it is used against all the bands in the other image. If
# the images have the same number of bands, but not the same names, they're
# used pairwise in the natural order. The output bands are named for the
# longer of the two inputs, or if they're equal in length, in image1's order.
# The type of the output pixels is the union of the input types.
#
# Args:
#   image1: The image from which the left operand bands are taken.
#   image2: The image from which the right operand bands are taken.
signatures.append({'args': [{'description': 'The image from which the left operand bands are taken.', 'name': 'image1', 'type': 'Image'}, {'description': 'The image from which the right operand bands are taken.', 'name': 'image2', 'type': 'Image'}], 'description': "Calculates the remainder of the first value divided by the second for each matched pair of bands in image1 and image2. If either image1 or image2 has only 1 band, then it is used against all the bands in the other image. If the images have the same number of bands, but not the same names, they're used pairwise in the natural order. The output bands are named for the longer of the two inputs, or if they're equal in length, in image1's order. The type of the output pixels is the union of the input types.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.mod'})
# Image.multiply
# Multiplies the first value by the second for each matched pair of bands in
# image1 and image2. If either image1 or image2 has only 1 band, then it is
# used against all the bands in the other image. If the images have the same
# number of bands, but not the same names, they're used pairwise in the
# natural order. The output bands are named for the longer of the two inputs,
# or if they're equal in length, in image1's order. The type of the output
# pixels is the union of the input types.
#
# Args:
#   image1: The image from which the left operand bands are taken.
#   image2: The image from which the right operand bands are taken.
signatures.append({'args': [{'description': 'The image from which the left operand bands are taken.', 'name': 'image1', 'type': 'Image'}, {'description': 'The image from which the right operand bands are taken.', 'name': 'image2', 'type': 'Image'}], 'description': "Multiplies the first value by the second for each matched pair of bands in image1 and image2. If either image1 or image2 has only 1 band, then it is used against all the bands in the other image. If the images have the same number of bands, but not the same names, they're used pairwise in the natural order. The output bands are named for the longer of the two inputs, or if they're equal in length, in image1's order. The type of the output pixels is the union of the input types.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.multiply'})
# Image.neighborhoodToArray
# Turns the neighborhood of each pixel in a scalar image into a 2D array.
# Axes 0 and 1 of the output array correspond to Y and X axes of the image,
# respectively. The output image will have as many bands as the input; each
# output band has the same mask as the corresponding input band. The
# footprint and metadata of the input image are preserved.
#
# Args:
#   image: The image to get pixels from; must be scalar-valued.
#   kernel: The kernel specifying the shape of the neighborhood.
#       Only fixed, square and rectangle kernels are supported.
#       Weights are ignored; only the shape of the kernel is used.
#   defaultValue: The value to use in the output arrays to
#       replace the invalid (masked) pixels of the input. If
#       the band type is integral, the fractional part of
#       this value is discarded; in all cases, the value is
#       clamped to the value range of the band.
signatures.append({'args': [{'description': 'The image to get pixels from; must be scalar-valued.', 'name': 'image', 'type': 'Image'}, {'description': 'The kernel specifying the shape of the neighborhood. Only fixed, square and rectangle kernels are supported. Weights are ignored; only the shape of the kernel is used.', 'name': 'kernel', 'type': 'Kernel'}, {'default': 0.0, 'description': 'The value to use in the output arrays to replace the invalid (masked) pixels of the input. If the band type is integral, the fractional part of this value is discarded; in all cases, the value is clamped to the value range of the band.', 'name': 'defaultValue', 'optional': True, 'type': 'Float'}], 'description': 'Turns the neighborhood of each pixel in a scalar image into a 2D array. Axes 0 and 1 of the output array correspond to Y and X axes of the image, respectively. The output image will have as many bands as the input; each output band has the same mask as the corresponding input band. The footprint and metadata of the input image are preserved.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.neighborhoodToArray'})
# Image.neighborhoodToBands
# Turn the neighborhood of a pixel into a set of bands. The neighborhood is
# specified using a Kernel, and only non-zero-weight kernel values are used.
# The weights of the kernel is otherwise ignored.  Each input band produces x
# * y output bands.  Each output band is named 'input_x_y' where x and y
# indicate the pixel's location in the kernel. For example, a 3x3 kernel
# operating on a 2-band image produces 18 output bands.
#
# Args:
#   image: The image to get pixels from.
#   kernel: The kernel specifying the neighborhood. Zero-weight
#       values are ignored.
signatures.append({'args': [{'description': 'The image to get pixels from.', 'name': 'image', 'type': 'Image'}, {'description': 'The kernel specifying the neighborhood. Zero-weight values are ignored.', 'name': 'kernel', 'type': 'Kernel'}], 'description': "Turn the neighborhood of a pixel into a set of bands. The neighborhood is specified using a Kernel, and only non-zero-weight kernel values are used. The weights of the kernel is otherwise ignored.\n\nEach input band produces x * y output bands.  Each output band is named 'input_x_y' where x and y indicate the pixel's location in the kernel. For example, a 3x3 kernel operating on a 2-band image produces 18 output bands.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.neighborhoodToBands'})
# Image.neq
# Returns 1 iff the first value is not equal to the second for each matched
# pair of bands in image1 and image2. If either image1 or image2 has only 1
# band, then it is used against all the bands in the other image. If the
# images have the same number of bands, but not the same names, they're used
# pairwise in the natural order. The output bands are named for the longer of
# the two inputs, or if they're equal in length, in image1's order. The type
# of the output pixels is boolean.
#
# Args:
#   image1: The image from which the left operand bands are taken.
#   image2: The image from which the right operand bands are taken.
signatures.append({'args': [{'description': 'The image from which the left operand bands are taken.', 'name': 'image1', 'type': 'Image'}, {'description': 'The image from which the right operand bands are taken.', 'name': 'image2', 'type': 'Image'}], 'description': "Returns 1 iff the first value is not equal to the second for each matched pair of bands in image1 and image2. If either image1 or image2 has only 1 band, then it is used against all the bands in the other image. If the images have the same number of bands, but not the same names, they're used pairwise in the natural order. The output bands are named for the longer of the two inputs, or if they're equal in length, in image1's order. The type of the output pixels is boolean.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.neq'})
# Image.normalizedDifference
# Computes the normalized difference between two bands. If the bands to use
# are not specified, uses the first two bands. The normalized difference is
# computed as (first − second) / (first + second).
#
# Args:
#   input: The input image.
#   bandNames: A list of names specifying the bands to use.  If
#       not specified, the first and second bands are used.
signatures.append({'args': [{'description': 'The input image.', 'name': 'input', 'type': 'Image'}, {'default': None, 'description': 'A list of names specifying the bands to use.  If not specified, the first and second bands are used.', 'name': 'bandNames', 'optional': True, 'type': 'List'}], 'description': 'Computes the normalized difference between two bands. If the bands to use are not specified, uses the first two bands. The normalized difference is computed as (first − second) / (first + second).', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.normalizedDifference'})
# Image.not
# Returns 0 if the input is non-zero, and 1 otherwise.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Returns 0 if the input is non-zero, and 1 otherwise.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.not'})
# Image.or
# Returns 1 iff either input value is non-zero for each matched pair of bands
# in image1 and image2. If either image1 or image2 has only 1 band, then it
# is used against all the bands in the other image. If the images have the
# same number of bands, but not the same names, they're used pairwise in the
# natural order. The output bands are named for the longer of the two inputs,
# or if they're equal in length, in image1's order. The type of the output
# pixels is boolean.
#
# Args:
#   image1: The image from which the left operand bands are taken.
#   image2: The image from which the right operand bands are taken.
signatures.append({'args': [{'description': 'The image from which the left operand bands are taken.', 'name': 'image1', 'type': 'Image'}, {'description': 'The image from which the right operand bands are taken.', 'name': 'image2', 'type': 'Image'}], 'description': "Returns 1 iff either input value is non-zero for each matched pair of bands in image1 and image2. If either image1 or image2 has only 1 band, then it is used against all the bands in the other image. If the images have the same number of bands, but not the same names, they're used pairwise in the natural order. The output bands are named for the longer of the two inputs, or if they're equal in length, in image1's order. The type of the output pixels is boolean.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.Or'})
# Image.paint
# Paints the geometries of a collection onto an image.
#
# Args:
#   image: The image on which the collection is painted.
#   featureCollection: The collection painted onto the
#       image.
#   color: Either the name of a color property or a number.
#   width: Either the name of a line-width property or a number.
signatures.append({'args': [{'description': 'The image on which the collection is painted.', 'name': 'image', 'type': 'Image'}, {'description': 'The collection painted onto the image.', 'name': 'featureCollection', 'type': 'FeatureCollection'}, {'default': 0, 'description': 'Either the name of a color property or a number.', 'name': 'color', 'optional': True, 'type': 'Object'}, {'default': None, 'description': 'Either the name of a line-width property or a number.', 'name': 'width', 'optional': True, 'type': 'Object'}], 'description': 'Paints the geometries of a collection onto an image.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.paint'})
# Image.parseExpression
# Generates an algorithm from an arithmetic expression on images. By default
# the generated algorithm takes one argument to denote the 'default' image.
# Other variables in the expression are interpreted as image arguments that
# will be passed to the returned algorithm. The bands of each image can be
# accessed as image.band_name or image[0]. The bands of the default image are
# available using the built-in function b(), as b(0) or b('band_name').  Both
# b() and image[] allow multiple arguments, to specify multiple bands, such
# as b(1, 'name', 3).  Calling b() with no arguments returns all bands of the
# image.
#
# Args:
#   expression: The expression to parse.
#   argName: The name of the default image argument.
#   vars: The parameters the resulting algorithm should have, which
#       must be a superset of the free variables in the expression,
#       including the default image argument if it is used.
signatures.append({'args': [{'description': 'The expression to parse.', 'name': 'expression', 'type': 'String'}, {'description': 'The name of the default image argument.', 'name': 'argName', 'type': 'String'}, {'description': 'The parameters the resulting algorithm should have, which must be a superset of the free variables in the expression, including the default image argument if it is used.', 'name': 'vars', 'type': 'List'}], 'description': "Generates an algorithm from an arithmetic expression on images. By default the generated algorithm takes one argument to denote the 'default' image. Other variables in the expression are interpreted as image arguments that will be passed to the returned algorithm. The bands of each image can be accessed as image.band_name or image[0]. The bands of the default image are available using the built-in function b(), as b(0) or b('band_name').  Both b() and image[] allow multiple arguments, to specify multiple bands, such as b(1, 'name', 3).  Calling b() with no arguments returns all bands of the image.", 'returns': 'Algorithm', 'type': 'Algorithm', 'hidden': True, 'name': 'Image.parseExpression'})
# Image.pixelArea
# Generate an image in which the value of each pixel is the area of that
# pixel in square meters.
signatures.append({'args': [], 'description': 'Generate an image in which the value of each pixel is the area of that pixel in square meters.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.pixelArea'})
# Image.pixelCoordinates
# Creates a two band image containing the x and y coordinates of each pixel
# in the given projection.
#
# Args:
#   projection: The projection in which to provide pixel.
signatures.append({'args': [{'description': 'The projection in which to provide pixel.', 'name': 'projection', 'type': 'Projection'}], 'description': 'Creates a two band image containing the x and y coordinates of each pixel in the given projection.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.pixelCoordinates'})
# Image.pixelLonLat
# Creates a two band image containing the longitude and latitude at each
# pixel, in degrees.
signatures.append({'args': [], 'description': 'Creates a two band image containing the longitude and latitude at each pixel, in degrees.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.pixelLonLat'})
# Image.polynomial
# Compute a polynomial at each pixel using the given coefficients.
#
# Args:
#   image: The input image.
#   coefficients: The polynomial coefficients in increasing
#       order of degree starting with the constant term.
signatures.append({'args': [{'description': 'The input image.', 'name': 'image', 'type': 'Image'}, {'description': 'The polynomial coefficients in increasing order of degree starting with the constant term.', 'name': 'coefficients', 'type': 'List'}], 'description': 'Compute a polynomial at each pixel using the given coefficients.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.polynomial'})
# Image.pow
# Raises the first value to the power of the second for each matched pair of
# bands in image1 and image2. If either image1 or image2 has only 1 band,
# then it is used against all the bands in the other image. If the images
# have the same number of bands, but not the same names, they're used
# pairwise in the natural order. The output bands are named for the longer of
# the two inputs, or if they're equal in length, in image1's order. The type
# of the output pixels is float.
#
# Args:
#   image1: The image from which the left operand bands are taken.
#   image2: The image from which the right operand bands are taken.
signatures.append({'args': [{'description': 'The image from which the left operand bands are taken.', 'name': 'image1', 'type': 'Image'}, {'description': 'The image from which the right operand bands are taken.', 'name': 'image2', 'type': 'Image'}], 'description': "Raises the first value to the power of the second for each matched pair of bands in image1 and image2. If either image1 or image2 has only 1 band, then it is used against all the bands in the other image. If the images have the same number of bands, but not the same names, they're used pairwise in the natural order. The output bands are named for the longer of the two inputs, or if they're equal in length, in image1's order. The type of the output pixels is float.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.pow'})
# Image.projection
# Returns the default projection of an Image.  Throws an error if the bands
# of the image don't all have the same projection.
#
# Args:
#   image: The image from which to get the projection.
signatures.append({'args': [{'description': 'The image from which to get the projection.', 'name': 'image', 'type': 'Image'}], 'description': "Returns the default projection of an Image.  Throws an error if the bands of the image don't all have the same projection.", 'returns': 'Projection', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.projection'})
# Image.random
# Generates a uniform random number at each pixel location, in the range of 0
# to 1.
#
# Args:
#   seed: Seed for the random number generator.
signatures.append({'args': [{'default': 0, 'description': 'Seed for the random number generator.', 'name': 'seed', 'optional': True, 'type': 'Long'}], 'description': 'Generates a uniform random number at each pixel location, in the range of 0 to 1.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.random'})
# Image.randomVisualizer
# Creates a vizualization image by assigning a random color to each unique
# value of the pixels of the first band. The first three bands of the output
# image will contan 8-bit R, G and B values, followed by all bands of the
# input image.
#
# Args:
#   image: Image with at least one band.
signatures.append({'args': [{'description': 'Image with at least one band.', 'name': 'image', 'type': 'Image'}], 'description': 'Creates a vizualization image by assigning a random color to each unique value of the pixels of the first band. The first three bands of the output image will contan 8-bit R, G and B values, followed by all bands of the input image.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.randomVisualizer'})
# Image.reduce
# Applies a reducer to all of the bands of an image. The reducer must have a
# single input and will be called at each pixel to reduce the stack of band
# values. The output image will have one band for each reducer output.
#
# Args:
#   image: The image to reduce.
#   reducer: The reducer to apply to the given image.
signatures.append({'args': [{'description': 'The image to reduce.', 'name': 'image', 'type': 'Image'}, {'description': 'The reducer to apply to the given image.', 'name': 'reducer', 'type': 'Reducer'}], 'description': 'Applies a reducer to all of the bands of an image.\nThe reducer must have a single input and will be called at each pixel to reduce the stack of band values.\nThe output image will have one band for each reducer output.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.reduce'})
# Image.reduceConnectedComponents
# Applies a reducer to all of the pixels inside of each 'object'. Pixels are
# considered to belong to an object if they are connected (8-way) and have
# the same value in the 'label' band.  The label band is only used to
# identify the connectedness; the rest are provided as inputs to the reducer.
#
# Args:
#   image: The input image.
#   reducer: The reducer to apply to pixels within the connected
#       component.
#   labelBand: The name of the band to use to detect
#       connectedness.  If unspecified, the first band is used.
#   maxSize: Size of the neighborhood to consider when aggregating
#       values.  Any objects larger than maxSize in either the
#       horizontal or vertical dimension will be masked, since
#       portions of the object might be outside of the
#       neighborhood.
signatures.append({'args': [{'description': 'The input image.', 'name': 'image', 'type': 'Image'}, {'description': 'The reducer to apply to pixels within the connected component.', 'name': 'reducer', 'type': 'Reducer'}, {'default': None, 'description': 'The name of the band to use to detect connectedness.  If unspecified, the first band is used.', 'name': 'labelBand', 'optional': True, 'type': 'String'}, {'default': 256, 'description': 'Size of the neighborhood to consider when aggregating values.  Any objects larger than maxSize in either the horizontal or vertical dimension will be masked, since portions of the object might be outside of the neighborhood.', 'name': 'maxSize', 'optional': True, 'type': 'Integer'}], 'description': "Applies a reducer to all of the pixels inside of each 'object'. Pixels are considered to belong to an object if they are connected (8-way) and have the same value in the 'label' band.  The label band is only used to identify the connectedness; the rest are provided as inputs to the reducer.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.reduceConnectedComponents'})
# Image.reduceNeighborhood
# Applies the given reducer to the neighborhood around each pixel, as
# determined by the given kernel. If the reducer has a single input, it will
# be applied separately to each band of the collection; otherwise it must
# have the same number of inputs as the input image has bands. The reducer
# output names determine the names of the output bands: reducers with
# multiple inputs will use the output names directly, while reducers with a
# single input will prefix the output name with the input band name (e.g.
# '10_mean', '20_mean', etc.). Reducers with weighted inputs can have the
# input weight based on the input mask, the kernel value, or the smaller of
# those two.
#
# Args:
#   image: The input image.
#   reducer: The reducer to apply to pixels within the
#       neighborhood.
#   kernel: The kernel defining the neighborhood.
#   inputWeight: One of 'mask', 'kernel', or 'min'.
#   skipMasked: Mask output pixels if the corresponding input
#       pixel is masked.
#   optimization: Optimization strategy.  Options are
#       'boxcar' and 'window'.  The 'boxcar' method is a fast
#       method for computing count, sum or mean.  It requires
#       a homogeneous kernel, a single-input reducer and
#       either MASK, KERNEL or no weighting. The 'window'
#       method uses a running window, and has the same
#       requirements as 'boxcar', but can use any single
#       input reducer.  Both methods require considerable
#       additional memory.
signatures.append({'args': [{'description': 'The input image.', 'name': 'image', 'type': 'Image'}, {'description': 'The reducer to apply to pixels within the neighborhood.', 'name': 'reducer', 'type': 'Reducer'}, {'description': 'The kernel defining the neighborhood.', 'name': 'kernel', 'type': 'Kernel'}, {'default': 'kernel', 'description': "One of 'mask', 'kernel', or 'min'.", 'name': 'inputWeight', 'optional': True, 'type': 'String'}, {'default': True, 'description': 'Mask output pixels if the corresponding input pixel is masked.', 'name': 'skipMasked', 'optional': True, 'type': 'Boolean'}, {'default': None, 'description': "Optimization strategy.  Options are 'boxcar' and 'window'.  The 'boxcar' method is a fast method for computing count, sum or mean.  It requires a homogeneous kernel, a single-input reducer and either MASK, KERNEL or no weighting. The 'window' method uses a running window, and has the same requirements as 'boxcar', but can use any single input reducer.  Both methods require considerable additional memory.", 'name': 'optimization', 'optional': True, 'type': 'String'}], 'description': "Applies the given reducer to the neighborhood around each pixel, as determined by the given kernel. If the reducer has a single input, it will be applied separately to each band of the collection; otherwise it must have the same number of inputs as the input image has bands.\nThe reducer output names determine the names of the output bands: reducers with multiple inputs will use the output names directly, while reducers with a single input will prefix the output name with the input band name (e.g. '10_mean', '20_mean', etc.).\nReducers with weighted inputs can have the input weight based on the input mask, the kernel value, or the smaller of those two.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.reduceNeighborhood'})
# Image.reduceRegion
# Apply a reducer to all the pixels in a specific region. Either the reducer
# must have the same number of inputs as the input image has bands, or it
# must have a single input and will be repeated for each band. Returns a
# dictionary of the reducer's outputs.
#
# Args:
#   image: The image to reduce.
#   reducer: The reducer to apply.
#   geometry: The region over which to reduce data.  Defaults to
#       the footprint of the image's first band.
#   scale: A nominal scale in meters of the projection to work in.
#   crs: The projection to work in. If unspecified, the projection of
#       the image's first band is used. If specified in addition to
#       scale, rescaled to the specified scale.
#   crsTransform: The list of CRS transform values.  This is
#       a row-major ordering of the 3x2 transform matrix.
#       This option is mutually exclusive with 'scale', and
#       replaces any transform already set on the projection.
#   bestEffort: If the polygon would contain too many pixels at
#       the given scale, compute and use a larger scale which
#       would allow the operation to succeed.
#   maxPixels: The maximum number of pixels to reduce.
#   tileScale: A scaling factor used to reduce aggregation tile
#       size; using a larger tileScale (e.g. 2 or 4) may enable
#       computations that run out of memory with the default.
signatures.append({'args': [{'description': 'The image to reduce.', 'name': 'image', 'type': 'Image'}, {'description': 'The reducer to apply.', 'name': 'reducer', 'type': 'Reducer'}, {'default': None, 'description': "The region over which to reduce data.  Defaults to the footprint of the image's first band.", 'name': 'geometry', 'optional': True, 'type': 'Geometry'}, {'default': None, 'description': 'A nominal scale in meters of the projection to work in.', 'name': 'scale', 'optional': True, 'type': 'Float'}, {'default': None, 'description': "The projection to work in. If unspecified, the projection of the image's first band is used. If specified in addition to scale, rescaled to the specified scale.", 'name': 'crs', 'optional': True, 'type': 'Projection'}, {'default': None, 'description': "The list of CRS transform values.  This is a row-major ordering of the 3x2 transform matrix.  This option is mutually exclusive with 'scale', and replaces any transform already set on the projection.", 'name': 'crsTransform', 'optional': True, 'type': 'List'}, {'default': False, 'description': 'If the polygon would contain too many pixels at the given scale, compute and use a larger scale which would allow the operation to succeed.', 'name': 'bestEffort', 'optional': True, 'type': 'Boolean'}, {'default': 10000000, 'description': 'The maximum number of pixels to reduce.', 'name': 'maxPixels', 'optional': True, 'type': 'Long'}, {'default': 1.0, 'description': 'A scaling factor used to reduce aggregation tile size; using a larger tileScale (e.g. 2 or 4) may enable computations that run out of memory with the default.', 'name': 'tileScale', 'optional': True, 'type': 'Float'}], 'description': "Apply a reducer to all the pixels in a specific region.\nEither the reducer must have the same number of inputs as the input image has bands, or it must have a single input and will be repeated for each band.\nReturns a dictionary of the reducer's outputs.", 'returns': 'Dictionary', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.reduceRegion'})
# Image.reduceRegions
# Apply a reducer over the area of each feature in the given collection. The
# reducer must have the same number of inputs as the input image has bands.
# Returns the input features, each augmented with the corresponding reducer
# outputs.
#
# Args:
#   image: The image to reduce.
#   collection: The features to reduce over.
#   reducer: The reducer to apply.
#   scale: A nominal scale in meters of the projection to work in.
#   crs: The projection to work in. If unspecified, the projection of
#       the image's first band is used. If specified in addition to
#       scale, rescaled to the specified scale.
#   crsTransform: The list of CRS transform values.  This is
#       a row-major ordering of the 3x2 transform matrix.
#       This option is mutually exclusive with 'scale', and
#       will replace any transform already set on the
#       projection.
#   tileScale: A scaling factor used to reduce aggregation tile
#       size; using a larger tileScale (e.g. 2 or 4) may enable
#       computations that run out of memory with the default.
signatures.append({'args': [{'description': 'The image to reduce.', 'name': 'image', 'type': 'Image'}, {'description': 'The features to reduce over.', 'name': 'collection', 'type': 'FeatureCollection'}, {'description': 'The reducer to apply.', 'name': 'reducer', 'type': 'Reducer'}, {'default': None, 'description': 'A nominal scale in meters of the projection to work in.', 'name': 'scale', 'optional': True, 'type': 'Float'}, {'default': None, 'description': "The projection to work in. If unspecified, the projection of the image's first band is used. If specified in addition to scale, rescaled to the specified scale.", 'name': 'crs', 'optional': True, 'type': 'Projection'}, {'default': None, 'description': "The list of CRS transform values.  This is a row-major ordering of the 3x2 transform matrix.  This option is mutually exclusive with 'scale', and will replace any transform already set on the projection.", 'name': 'crsTransform', 'optional': True, 'type': 'List'}, {'default': 1.0, 'description': 'A scaling factor used to reduce aggregation tile size; using a larger tileScale (e.g. 2 or 4) may enable computations that run out of memory with the default.', 'name': 'tileScale', 'optional': True, 'type': 'Float'}], 'description': 'Apply a reducer over the area of each feature in the given collection.\nThe reducer must have the same number of inputs as the input image has bands.\nReturns the input features, each augmented with the corresponding reducer outputs.', 'returns': 'FeatureCollection', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.reduceRegions'})
# Image.reduceResolution
# Enables reprojection using the given reducer to combine all input pixels
# corresponding to each output pixel. If the reducer has a single input, it
# will be applied separately to each band of the collection; otherwise it
# must have the same number of inputs as the input image has bands. The
# reducer output names determine the names of the output bands: reducers with
# multiple inputs will use the output names directly, reducers with a single
# input and single output will preserve the input band names, and reducers
# with a single input and multiple outputs will prefix the output name with
# the input band name (e.g. '10_mean', '10_stdDev', '20_mean', '20_stdDev',
# etc.). Reducer input weights will be the product of the  input mask and the
# fraction of the output pixel covered by the input pixel.
#
# Args:
#   image: The input image.
#   reducer: The reducer to apply to be used for combining pixels.
#   bestEffort: If using the input at its default resolution
#       would require too many pixels, start with already-
#       reduced input pixels from a pyramid level that allows
#       the operation to succeed.
#   maxPixels: The maximum number of input pixels to combine for
#       each output pixel.  Setting this too large will cause
#       out-of-memory problems.
signatures.append({'args': [{'description': 'The input image.', 'name': 'image', 'type': 'Image'}, {'description': 'The reducer to apply to be used for combining pixels.', 'name': 'reducer', 'type': 'Reducer'}, {'default': False, 'description': 'If using the input at its default resolution would require too many pixels, start with already-reduced input pixels from a pyramid level that allows the operation to succeed.', 'name': 'bestEffort', 'optional': True, 'type': 'Boolean'}, {'default': 64, 'description': 'The maximum number of input pixels to combine for each output pixel.  Setting this too large will cause out-of-memory problems.', 'name': 'maxPixels', 'optional': True, 'type': 'Integer'}], 'description': "Enables reprojection using the given reducer to combine all input pixels corresponding to each output pixel. If the reducer has a single input, it will be applied separately to each band of the collection; otherwise it must have the same number of inputs as the input image has bands.\nThe reducer output names determine the names of the output bands: reducers with multiple inputs will use the output names directly, reducers with a single input and single output will preserve the input band names, and reducers with a single input and multiple outputs will prefix the output name with the input band name (e.g. '10_mean', '10_stdDev', '20_mean', '20_stdDev', etc.).\nReducer input weights will be the product of the  input mask and the fraction of the output pixel covered by the input pixel.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.reduceResolution'})
# Image.reduceToVectors
# Convert an image to a feature collection by reducing homogenous regions.
# Given an image containing a band of labeled segments and zero or more
# additional bands, runs a reducer over the pixels in each segment producing
# a feature per segment. Either the reducer must have one fewer inputs than
# the image has bands, or it must have a single input and will be repeated
# for each band.
#
# Args:
#   image: The input image. The first band is expected to be an
#       integer type; adjacent pixels will be in the same segment if
#       they have the same value in this band.
#   reducer: The reducer to apply.  Its inputs will be taken from
#       the image's bands after dropping the first band.  Defaults
#       to Reducer.countEvery()
#   geometry: The region over which to reduce data.  Defaults to
#       the footprint of the image's first band.
#   scale: A nominal scale in meters of the projection to work in.
#   geometryType: How to choose the geometry of each
#       generated feature; one of 'polygon' (a polygon
#       enclosing the pixels in the segment), 'bb' (a
#       rectangle bounding the pixels), or 'centroid' (the
#       centroid of the pixels).
#   eightConnected: If true, diagonally-connected pixels
#       are considered adjacent; otherwise only pixels that
#       share an edge are.
#   labelProperty: If non-null, the value of the first band
#       will be saved as the specified property of each
#       feature.
#   crs: The projection to work in. If unspecified, the projection of
#       the image's first band is used. If specified in addition to
#       scale, rescaled to the specified scale.
#   crsTransform: The list of CRS transform values.  This is
#       a row-major ordering of the 3x2 transform matrix.
#       This option is mutually exclusive with 'scale', and
#       replaces any transform already set on the projection.
#   bestEffort: If the polygon would contain too many pixels at
#       the given scale, compute and use a larger scale which
#       would allow the operation to succeed.
#   maxPixels: The maximum number of pixels to reduce.
#   tileScale: A scaling factor used to reduce aggregation tile
#       size; using a larger tileScale (e.g. 2 or 4) may enable
#       computations that run out of memory with the default.
#   geometryInNativeProjection: Create
#       geometries in the pixel projection,
#       rather than WGS84.
signatures.append({'args': [{'description': 'The input image. The first band is expected to be an integer type; adjacent pixels will be in the same segment if they have the same value in this band.', 'name': 'image', 'type': 'Image'}, {'default': None, 'description': "The reducer to apply.  Its inputs will be taken from the image's bands after dropping the first band.  Defaults to Reducer.countEvery()", 'name': 'reducer', 'optional': True, 'type': 'Reducer'}, {'default': None, 'description': "The region over which to reduce data.  Defaults to the footprint of the image's first band.", 'name': 'geometry', 'optional': True, 'type': 'Geometry'}, {'default': None, 'description': 'A nominal scale in meters of the projection to work in.', 'name': 'scale', 'optional': True, 'type': 'Float'}, {'default': 'polygon', 'description': "How to choose the geometry of each generated feature; one of 'polygon' (a polygon enclosing the pixels in the segment), 'bb' (a rectangle bounding the pixels), or 'centroid' (the centroid of the pixels).", 'name': 'geometryType', 'optional': True, 'type': 'String'}, {'default': True, 'description': 'If true, diagonally-connected pixels are considered adjacent; otherwise only pixels that share an edge are.', 'name': 'eightConnected', 'optional': True, 'type': 'Boolean'}, {'default': 'label', 'description': 'If non-null, the value of the first band will be saved as the specified property of each feature.', 'name': 'labelProperty', 'optional': True, 'type': 'String'}, {'default': None, 'description': "The projection to work in. If unspecified, the projection of the image's first band is used. If specified in addition to scale, rescaled to the specified scale.", 'name': 'crs', 'optional': True, 'type': 'Projection'}, {'default': None, 'description': "The list of CRS transform values.  This is a row-major ordering of the 3x2 transform matrix.  This option is mutually exclusive with 'scale', and replaces any transform already set on the projection.", 'name': 'crsTransform', 'optional': True, 'type': 'List'}, {'default': False, 'description': 'If the polygon would contain too many pixels at the given scale, compute and use a larger scale which would allow the operation to succeed.', 'name': 'bestEffort', 'optional': True, 'type': 'Boolean'}, {'default': 10000000, 'description': 'The maximum number of pixels to reduce.', 'name': 'maxPixels', 'optional': True, 'type': 'Long'}, {'default': 1.0, 'description': 'A scaling factor used to reduce aggregation tile size; using a larger tileScale (e.g. 2 or 4) may enable computations that run out of memory with the default.', 'name': 'tileScale', 'optional': True, 'type': 'Float'}, {'default': False, 'description': 'Create geometries in the pixel projection, rather than WGS84.', 'name': 'geometryInNativeProjection', 'optional': True, 'type': 'Boolean'}], 'description': 'Convert an image to a feature collection by reducing homogenous regions. Given an image containing a band of labeled segments and zero or more additional bands, runs a reducer over the pixels in each segment producing a feature per segment.\nEither the reducer must have one fewer inputs than the image has bands, or it must have a single input and will be repeated for each band.', 'returns': 'FeatureCollection', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.reduceToVectors'})
# Image.reduceToVectorsStreaming
# Convert an image to a feature collection by reducing homogenous regions.
# Given an image containing a band of labeled segments and zero or more
# additional bands, runs a reducer over the pixels in each segment producing
# a feature per segment. Either the reducer must have one fewer inputs than
# the image has bands, or it must have a single input and will be repeated
# for each band.
#
# Args:
#   image: The input image. The first band is expected to be an
#       integer type; adjacent pixels will be in the same segment if
#       they have the same value in this band.
#   reducer: The reducer to apply.  Its inputs will be taken from
#       the image's bands after dropping the first band.  Defaults
#       to Reducer.countEvery()
#   geometry: The region over which to reduce data.  Defaults to
#       the footprint of the image's first band.
#   scale: A nominal scale in meters of the projection to work in.
#   geometryType: How to choose the geometry of each
#       generated feature; one of 'polygon' (a polygon
#       enclosing the pixels in the segment), 'bb' (a
#       rectangle bounding the pixels), or 'centroid' (the
#       centroid of the pixels).
#   eightConnected: If true, diagonally-connected pixels
#       are considered adjacent; otherwise only pixels that
#       share an edge are.
#   labelProperty: If non-null, the value of the first band
#       will be saved as the specified property of each
#       feature.
#   crs: The projection to work in. If unspecified, the projection of
#       the image's first band is used. If specified in addition to
#       scale, rescaled to the specified scale.
#   crsTransform: The list of CRS transform values.  This is
#       a row-major ordering of the 3x2 transform matrix.
#       This option is mutually exclusive with 'scale', and
#       replaces any transform already set on the projection.
#   bestEffort: If the polygon would contain too many pixels at
#       the given scale, compute and use a larger scale which
#       would allow the operation to succeed.
#   maxPixels: The maximum number of pixels to reduce.
#   tileScale: A scaling factor used to reduce aggregation tile
#       size; using a larger tileScale (e.g. 2 or 4) may enable
#       computations that run out of memory with the default.
#   geometryInNativeProjection: Create
#       geometries in the pixel projection,
#       rather than WGS84.
signatures.append({'args': [{'description': 'The input image. The first band is expected to be an integer type; adjacent pixels will be in the same segment if they have the same value in this band.', 'name': 'image', 'type': 'Image'}, {'default': None, 'description': "The reducer to apply.  Its inputs will be taken from the image's bands after dropping the first band.  Defaults to Reducer.countEvery()", 'name': 'reducer', 'optional': True, 'type': 'Reducer'}, {'default': None, 'description': "The region over which to reduce data.  Defaults to the footprint of the image's first band.", 'name': 'geometry', 'optional': True, 'type': 'Geometry'}, {'default': None, 'description': 'A nominal scale in meters of the projection to work in.', 'name': 'scale', 'optional': True, 'type': 'Float'}, {'default': 'polygon', 'description': "How to choose the geometry of each generated feature; one of 'polygon' (a polygon enclosing the pixels in the segment), 'bb' (a rectangle bounding the pixels), or 'centroid' (the centroid of the pixels).", 'name': 'geometryType', 'optional': True, 'type': 'String'}, {'default': True, 'description': 'If true, diagonally-connected pixels are considered adjacent; otherwise only pixels that share an edge are.', 'name': 'eightConnected', 'optional': True, 'type': 'Boolean'}, {'default': 'label', 'description': 'If non-null, the value of the first band will be saved as the specified property of each feature.', 'name': 'labelProperty', 'optional': True, 'type': 'String'}, {'default': None, 'description': "The projection to work in. If unspecified, the projection of the image's first band is used. If specified in addition to scale, rescaled to the specified scale.", 'name': 'crs', 'optional': True, 'type': 'Projection'}, {'default': None, 'description': "The list of CRS transform values.  This is a row-major ordering of the 3x2 transform matrix.  This option is mutually exclusive with 'scale', and replaces any transform already set on the projection.", 'name': 'crsTransform', 'optional': True, 'type': 'List'}, {'default': False, 'description': 'If the polygon would contain too many pixels at the given scale, compute and use a larger scale which would allow the operation to succeed.', 'name': 'bestEffort', 'optional': True, 'type': 'Boolean'}, {'default': 10000000, 'description': 'The maximum number of pixels to reduce.', 'name': 'maxPixels', 'optional': True, 'type': 'Long'}, {'default': 1.0, 'description': 'A scaling factor used to reduce aggregation tile size; using a larger tileScale (e.g. 2 or 4) may enable computations that run out of memory with the default.', 'name': 'tileScale', 'optional': True, 'type': 'Float'}, {'default': False, 'description': 'Create geometries in the pixel projection, rather than WGS84.', 'name': 'geometryInNativeProjection', 'optional': True, 'type': 'Boolean'}], 'description': 'Convert an image to a feature collection by reducing homogenous regions. Given an image containing a band of labeled segments and zero or more additional bands, runs a reducer over the pixels in each segment producing a feature per segment.\nEither the reducer must have one fewer inputs than the image has bands, or it must have a single input and will be repeated for each band.', 'returns': 'FeatureCollection', 'type': 'Algorithm', 'hidden': True, 'name': 'Image.reduceToVectorsStreaming'})
# Image.regexpRename
# Renames the bands of an image by applying a regular expression replacement
# to the current band names.  Any bands not matched by the regex will be
# copied over without renaming.
#
# Args:
#   input: The image containing the bands to rename.
#   regex: A regular expression to match in each band name.
#   replacement: The text with which to replace each match.
#       Supports $n syntax for captured values.
#   all: If true, all matches in a given string will be replaced.
#       Otherwise, only the first match in each string will be
#       replaced.
signatures.append({'args': [{'description': 'The image containing the bands to rename.', 'name': 'input', 'type': 'Image'}, {'description': 'A regular expression to match in each band name.', 'name': 'regex', 'type': 'String'}, {'description': 'The text with which to replace each match.  Supports $n syntax for captured values.', 'name': 'replacement', 'type': 'String'}, {'default': True, 'description': 'If true, all matches in a given string will be replaced.  Otherwise, only the first match in each string will be replaced.', 'name': 'all', 'optional': True, 'type': 'Boolean'}], 'description': 'Renames the bands of an image by applying a regular expression replacement to the current band names.  Any bands not matched by the regex will be copied over without renaming.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.regexpRename'})
# Image.register
# Registers an image to a reference image while allowing local, rubber sheet
# deformations. Displacements are computed in the CRS of the reference image,
# at a scale dictated by the lowest resolution of the following three
# projections: input image projection, reference image projection, and
# requested projection. The displacements then applied to the input image to
# register it with the reference.
#
# Args:
#   image: The image to register.
#   referenceImage: The image to register to.
#   maxOffset: The maximum offset allowed when attempting to
#       align the input images, in meters. Using a smaller value
#       can reduce computation time significantly, but it must
#       still be large enough to cover the greatest displacement
#       within the entire image region.
#   patchWidth: Patch size for detecting image offsets, in
#       meters. This should be set large enough to capture
#       texture, as well as large enough that ignorable objects
#       are small within the patch. Default is null. Patch size
#       will be determined automatically if notprovided.
#   stiffness: Enforces a stiffness constraint on the solution.
#       Valid values are in the range [0,10]. The stiffness is
#       used for outlier rejection when determining
#       displacements at adjacent grid points. Higher values
#       move the solution towards a rigid transformation. Lower
#       values allow more distortion or warping of the image
#       during registration.
signatures.append({'args': [{'description': 'The image to register.', 'name': 'image', 'type': 'Image'}, {'description': 'The image to register to.', 'name': 'referenceImage', 'type': 'Image'}, {'description': 'The maximum offset allowed when attempting to align the input images, in meters. Using a smaller value can reduce computation time significantly, but it must still be large enough to cover the greatest displacement within the entire image region.', 'name': 'maxOffset', 'type': 'Float'}, {'default': None, 'description': 'Patch size for detecting image offsets, in meters. This should be set large enough to capture texture, as well as large enough that ignorable objects are small within the patch. Default is null. Patch size will be determined automatically if notprovided.', 'name': 'patchWidth', 'optional': True, 'type': 'Float'}, {'default': 5.0, 'description': 'Enforces a stiffness constraint on the solution. Valid values are in the range [0,10]. The stiffness is used for outlier rejection when determining displacements at adjacent grid points. Higher values move the solution towards a rigid transformation. Lower values allow more distortion or warping of the image during registration.', 'name': 'stiffness', 'optional': True, 'type': 'Float'}], 'description': 'Registers an image to a reference image while allowing local, rubber sheet deformations. Displacements are computed in the CRS of the reference image, at a scale dictated by the lowest resolution of the following three projections: input image projection, reference image projection, and requested projection. The displacements then applied to the input image to register it with the reference.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.register'})
# Image.remap
# Maps from input values to output values, represented by two parallel lists.
# Any input values not included in the input list are either set to
# defaultValue if it is given, or masked if it isn't.  Note that inputs
# containing floating point values might sometimes fail to match due to
# floating point precision errors.
#
# Args:
#   image: The image to which the remapping is applied.
#   from: The source values (numbers or EEArrays). All values in this
#       list will be mapped to the corresponding value in 'to'.
#   to: The destination values (numbers or EEArrays). These are used to
#       replace the corresponding values in 'from'. Must have the same
#       number of values as 'from'.
#   defaultValue: The default value to replace values that
#       weren't matched by a value in 'from'. If not
#       specified, unmatched values are masked out.
#   bandName: The name of the band to remap. If not specified,
#       the first  band in the image is used.
signatures.append({'args': [{'description': 'The image to which the remapping is applied.', 'name': 'image', 'type': 'Image'}, {'description': "The source values (numbers or EEArrays). All values in this list will be mapped to the corresponding value in 'to'.", 'name': 'from', 'type': 'List'}, {'description': "The destination values (numbers or EEArrays). These are used to replace the corresponding values in 'from'. Must have the same number of values as 'from'.", 'name': 'to', 'type': 'List'}, {'default': None, 'description': "The default value to replace values that weren't matched by a value in 'from'. If not specified, unmatched values are masked out.", 'name': 'defaultValue', 'optional': True, 'type': 'Object'}, {'default': None, 'description': 'The name of the band to remap. If not specified, the first  band in the image is used.', 'name': 'bandName', 'optional': True, 'type': 'String'}], 'description': "Maps from input values to output values, represented by two parallel lists. Any input values not included in the input list are either set to defaultValue if it is given, or masked if it isn't.  Note that inputs containing floating point values might sometimes fail to match due to  floating point precision errors.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.remap'})
# Image.rename
# Renames the bands of an image.
#
# Args:
#   input: The image to select bands from.
#   names: New names for the image's bands.  Must exactly match the
#       number of bands in input.
signatures.append({'args': [{'description': 'The image to select bands from.', 'name': 'input', 'type': 'Image'}, {'description': "New names for the image's bands.  Must exactly match the number of bands in input.", 'name': 'names', 'type': 'List'}], 'description': 'Renames the bands of an image.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.rename'})
# Image.reproject
# Force an image to be computed in a given projection and  resolution.
#
# Args:
#   image: The Image to reproject.
#   crs: The CRS to project the image to.
#   crsTransform: The list of CRS transform values.  This is
#       a row-major ordering of the 3x2 transform matrix.
#       This option is mutually exclusive with the scale
#       option, and replaces any transform already on the
#       projection.
#   scale: If scale is specified, then the projection is scaled by
#       dividing the specified scale value by the nominal size of a
#       meter in the specified projection. If scale is not
#       specified, then the scale of the given projection will be
#       used.
signatures.append({'args': [{'description': 'The Image to reproject.', 'name': 'image', 'type': 'Image'}, {'description': 'The CRS to project the image to.', 'name': 'crs', 'type': 'Projection'}, {'default': None, 'description': 'The list of CRS transform values.  This is a row-major ordering of the 3x2 transform matrix.  This option is mutually exclusive with the scale option, and replaces any transform already on the projection.', 'name': 'crsTransform', 'optional': True, 'type': 'List'}, {'default': None, 'description': 'If scale is specified, then the projection is scaled by dividing the specified scale value by the nominal size of a meter in the specified projection. If scale is not specified, then the scale of the given projection will be used.', 'name': 'scale', 'optional': True, 'type': 'Float'}], 'description': 'Force an image to be computed in a given projection and  resolution.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.reproject'})
# Image.resample
# An algorithm that returns an image identical to its argument, but which
# uses bilinear or bicubic interpolation (rather than the default nearest-
# neighbor) to compute pixels in projections other than its native projection
# or other levels of the same image pyramid. This relies on the input image's
# default projection being meaningful, and so cannot be used on composites,
# for example. (Instead, you should resample the images that are used to
# create the composite.)
#
# Args:
#   image: The Image to resample.
#   mode: The interpolation mode to use.  One of 'bilinear' or
#       'bicubic'.)
signatures.append({'args': [{'description': 'The Image to resample.', 'name': 'image', 'type': 'Image'}, {'default': 'bilinear', 'description': "The interpolation mode to use.  One of 'bilinear' or 'bicubic'.)", 'name': 'mode', 'optional': True, 'type': 'String'}], 'description': "An algorithm that returns an image identical to its argument, but which uses bilinear or bicubic interpolation (rather than the default nearest-neighbor) to compute pixels in projections other than its native projection or other levels of the same image pyramid.\nThis relies on the input image's default projection being meaningful, and so cannot be used on composites, for example. (Instead, you should resample the images that are used to create the composite.)", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.resample'})
# Image.retile
# Change the size of tiles in which the input image is calculated.  When
# pixels of this image are needed, they are computed in tiles of the
# specified size. This allows a memory-intensive image computation, such as
# one involving large array bands, to be broken up into smaller pieces that
# will fit into memory where larger ones will not.  Currently, if the image
# is used in a reduce operation, the tileScale parameter should be used
# instead of retile(). retile() will also have no or detrimental effect in an
# Export.video task.
#
# Args:
#   image: Input image. The result will have the same bands and
#       properties.
#   size: Edge length in pixels of the tile grid to use; must be
#       between 1 and 256.
signatures.append({'args': [{'description': 'Input image. The result will have the same bands and properties.', 'name': 'image', 'type': 'Image'}, {'description': 'Edge length in pixels of the tile grid to use; must be between 1 and 256.', 'name': 'size', 'type': 'Integer'}], 'description': 'Change the size of tiles in which the input image is calculated.\n\nWhen pixels of this image are needed, they are computed in tiles of the specified size. This allows a memory-intensive image computation, such as one involving large array bands, to be broken up into smaller pieces that will fit into memory where larger ones will not.\n\nCurrently, if the image is used in a reduce operation, the tileScale parameter should be used instead of retile(). retile() will also have no or detrimental effect in an Export.video task.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.retile'})
# Image.rgbToHsv
# Transforms the image from the RGB color space to the HSV color space.
# Produces three bands: hue, saturation and value, all floating point values
# in the range [0, 1].
#
# Args:
#   image: The image to transform.
signatures.append({'args': [{'description': 'The image to transform.', 'name': 'image', 'type': 'Image'}], 'description': 'Transforms the image from the RGB color space to the HSV color space. Produces three bands: hue, saturation and value, all floating point values in the range [0, 1].', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.rgbToHsv'})
# Image.rightShift
# Calculates the signed right shift of v1 by v2 bits for each matched pair of
# bands in image1 and image2. If either image1 or image2 has only 1 band,
# then it is used against all the bands in the other image. If the images
# have the same number of bands, but not the same names, they're used
# pairwise in the natural order. The output bands are named for the longer of
# the two inputs, or if they're equal in length, in image1's order. The type
# of the output pixels is the union of the input types.
#
# Args:
#   image1: The image from which the left operand bands are taken.
#   image2: The image from which the right operand bands are taken.
signatures.append({'args': [{'description': 'The image from which the left operand bands are taken.', 'name': 'image1', 'type': 'Image'}, {'description': 'The image from which the right operand bands are taken.', 'name': 'image2', 'type': 'Image'}], 'description': "Calculates the signed right shift of v1 by v2 bits for each matched pair of bands in image1 and image2. If either image1 or image2 has only 1 band, then it is used against all the bands in the other image. If the images have the same number of bands, but not the same names, they're used pairwise in the natural order. The output bands are named for the longer of the two inputs, or if they're equal in length, in image1's order. The type of the output pixels is the union of the input types.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.rightShift'})
# Image.right_shift
# Calculates the signed right shift of v1 by v2 bits for each matched pair of
# bands in image1 and image2. If either image1 or image2 has only 1 band,
# then it is used against all the bands in the other image. If the images
# have the same number of bands, but not the same names, they're used
# pairwise in the natural order. The output bands are named for the longer of
# the two inputs, or if they're equal in length, in image1's order. The type
# of the output pixels is the union of the input types.
#
# Args:
#   image1: The image from which the left operand bands are taken.
#   image2: The image from which the right operand bands are taken.
signatures.append({'args': [{'description': 'The image from which the left operand bands are taken.', 'name': 'image1', 'type': 'Image'}, {'description': 'The image from which the right operand bands are taken.', 'name': 'image2', 'type': 'Image'}], 'description': "Calculates the signed right shift of v1 by v2 bits for each matched pair of bands in image1 and image2. If either image1 or image2 has only 1 band, then it is used against all the bands in the other image. If the images have the same number of bands, but not the same names, they're used pairwise in the natural order. The output bands are named for the longer of the two inputs, or if they're equal in length, in image1's order. The type of the output pixels is the union of the input types.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.right_shift'})
# Image.round
# Computes the integer nearest to the input.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Computes the integer nearest to the input.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.round'})
# Image.rsedTransform
# Computes the 2D maximal height surface created by placing an inverted
# parabola over each non-zero pixel of the input image, where the pixel's
# value is the height of the parabola.  Viewed as a binary image (zero/not-
# zero) this is equivalent to buffering each non-zero input pixel by the
# square root of its value, in pixels.
#
# Args:
#   image: The input image.
#   neighborhood: Neighborhood size in pixels.
#   units: The units of the neighborhood, currently only 'pixels'
#       are supported.
signatures.append({'args': [{'description': 'The input image.', 'name': 'image', 'type': 'Image'}, {'default': 256, 'description': 'Neighborhood size in pixels.', 'name': 'neighborhood', 'optional': True, 'type': 'Integer'}, {'default': 'pixels', 'description': "The units of the neighborhood, currently only 'pixels' are supported.", 'name': 'units', 'optional': True, 'type': 'String'}], 'description': "Computes the 2D maximal height surface created by placing an inverted parabola over each non-zero pixel of the input image, where the pixel's value is the height of the parabola.  Viewed as a binary image (zero/not-zero) this is equivalent to buffering each non-zero input pixel by the square root of its value, in pixels.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.rsedTransform'})
# Image.sample
# Samples the pixels of an image, returning them as a FeatureCollection. Each
# feature will have 1 property per band in the input image.
#
# Args:
#   image: The image to sample.
#   region: The region to sample from. If unspecified, uses the
#       image's whole footprint.
#   scale: A nominal scale in meters of the projection to sample in.
#   projection: The projection in which to sample. If
#       unspecified, the projection of the image's first band
#       is used. If specified in addition to scale, rescaled to
#       the specified scale.
#   factor: A subsampling factor, within (0, 1]. If specified,
#       'numPixels' must not be specified. Defaults to no
#       subsampling.
#   numPixels: The approximate number of pixels to sample. If
#       specified, 'factor' must not be specified.
#   seed: A randomization seed to use for subsampling.
#   dropNulls: Post filter the result to drop features that have
#       null-valued properties.
#   tileScale: A scaling factor used to reduce aggregation tile
#       size; using a larger tileScale (e.g. 2 or 4) may enable
#       computations that run out of memory with the default.
#   geometries: If true, adds the center of the sampled pixel
#       as the geometry property of the output feature.
#       Otherwise, geometries will be omitted (saving memory).
signatures.append({'args': [{'description': 'The image to sample.', 'name': 'image', 'type': 'Image'}, {'default': None, 'description': "The region to sample from. If unspecified, uses the image's whole footprint.", 'name': 'region', 'optional': True, 'type': 'Geometry'}, {'default': None, 'description': 'A nominal scale in meters of the projection to sample in.', 'name': 'scale', 'optional': True, 'type': 'Float'}, {'default': None, 'description': "The projection in which to sample. If unspecified, the projection of the image's first band is used. If specified in addition to scale, rescaled to the specified scale.", 'name': 'projection', 'optional': True, 'type': 'Projection'}, {'default': None, 'description': "A subsampling factor, within (0, 1]. If specified, 'numPixels' must not be specified. Defaults to no subsampling.", 'name': 'factor', 'optional': True, 'type': 'Float'}, {'default': None, 'description': "The approximate number of pixels to sample. If specified, 'factor' must not be specified.", 'name': 'numPixels', 'optional': True, 'type': 'Long'}, {'default': 0, 'description': 'A randomization seed to use for subsampling.', 'name': 'seed', 'optional': True, 'type': 'Integer'}, {'default': True, 'description': 'Post filter the result to drop features that have null-valued properties.', 'name': 'dropNulls', 'optional': True, 'type': 'Boolean'}, {'default': 1.0, 'description': 'A scaling factor used to reduce aggregation tile size; using a larger tileScale (e.g. 2 or 4) may enable computations that run out of memory with the default.', 'name': 'tileScale', 'optional': True, 'type': 'Float'}, {'default': False, 'description': 'If true, adds the center of the sampled pixel as the geometry property of the output feature.  Otherwise, geometries will be omitted (saving memory).', 'name': 'geometries', 'optional': True, 'type': 'Boolean'}], 'description': 'Samples the pixels of an image, returning them as a FeatureCollection. Each feature will have 1 property per band in the input image.', 'returns': 'FeatureCollection', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.sample'})
# Image.sampleRegions
# Samples the pixels of an image in one or more regions, returning them as a
# FeatureCollection.  Each output feature will have 1 property per band in
# the input image, as well as any specified properties copied from the input
# feature. Note that geometries will be snapped to pixel centers.
#
# Args:
#   image: The image to sample.
#   collection: The regions to sample over.
#   properties: The list of properties to copy from each input
#       feature.  Defaults to all non-system properties.
#   scale: A nominal scale in meters of the projection to sample in.
#       If unspecified,the scale of the image's first band is used.
#   projection: The projection in which to sample. If
#       unspecified, the projection of the image's first band
#       is used. If specified in addition to scale, rescaled to
#       the specified scale.
#   tileScale: A scaling factor used to reduce aggregation tile
#       size; using a larger tileScale (e.g. 2 or 4) may enable
#       computations that run out of memory with the default.
#   geometries: If true, the results will include a geometry
#       per sampled pixel.  Otherwise, geometries will be
#       omitted (saving memory).
signatures.append({'args': [{'description': 'The image to sample.', 'name': 'image', 'type': 'Image'}, {'description': 'The regions to sample over.', 'name': 'collection', 'type': 'FeatureCollection'}, {'default': None, 'description': 'The list of properties to copy from each input feature.  Defaults to all non-system properties.', 'name': 'properties', 'optional': True, 'type': 'List'}, {'default': None, 'description': "A nominal scale in meters of the projection to sample in.  If unspecified,the scale of the image's first band is used.", 'name': 'scale', 'optional': True, 'type': 'Float'}, {'default': None, 'description': "The projection in which to sample. If unspecified, the projection of the image's first band is used. If specified in addition to scale, rescaled to the specified scale.", 'name': 'projection', 'optional': True, 'type': 'Projection'}, {'default': 1.0, 'description': 'A scaling factor used to reduce aggregation tile size; using a larger tileScale (e.g. 2 or 4) may enable computations that run out of memory with the default.', 'name': 'tileScale', 'optional': True, 'type': 'Float'}, {'default': False, 'description': 'If true, the results will include a geometry per sampled pixel.  Otherwise, geometries will be omitted (saving memory).', 'name': 'geometries', 'optional': True, 'type': 'Boolean'}], 'description': 'Samples the pixels of an image in one or more regions, returning them as a FeatureCollection.  Each output feature will have 1 property per band in the input image, as well as any specified properties copied from the input feature. Note that geometries will be snapped to pixel centers.', 'returns': 'FeatureCollection', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.sampleRegions'})
# Image.select
# Selects bands from an image by name, RE2-compatible regex or index and
# optionally renames them.
#
# Args:
#   input: The image to select bands from.
#   bandSelectors: A list of names, regexes or numeric
#       indicies specifying the bands to select.
#   newNames: Optional new names for the output bands.  Must
#       match the number of bands selected.
signatures.append({'args': [{'description': 'The image to select bands from.', 'name': 'input', 'type': 'Image'}, {'description': 'A list of names, regexes or numeric indicies specifying the bands to select.', 'name': 'bandSelectors', 'type': 'List'}, {'default': None, 'description': 'Optional new names for the output bands.  Must match the number of bands selected.', 'name': 'newNames', 'optional': True, 'type': 'List'}], 'description': 'Selects bands from an image by name, RE2-compatible regex or index and optionally renames them.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.select'})
# Image.selfMask
# Updates an image's mask at all positions where the existing mask is not
# zero using the value of the image as the new mask value. The output image
# retains the metadata and footprint of the input image.
#
# Args:
#   image: The image to mask with itself.
signatures.append({'args': [{'description': 'The image to mask with itself.', 'name': 'image', 'type': 'Image'}], 'description': "Updates an image's mask at all positions where the existing mask is not zero using the value of the image as the new mask value. The output image retains the metadata and footprint of the input image.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.selfMask'})
# Image.short
# Casts the input value to a signed 16-bit integer.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Casts the input value to a signed 16-bit integer.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.short'})
# Image.sin
# Computes the sine of the input in radians.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Computes the sine of the input in radians.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.sin'})
# Image.sinh
# Computes the hyperbolic sine of the input.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Computes the hyperbolic sine of the input.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.sinh'})
# Image.sldStyle
# Styles a raster input with the provided OGC SLD styling.  Points of note:
# * OGC SLD 1.0 and OGC SE 1.1 are supported.  * The XML document passed in
# can be complete, or just the   SldRasterSymbolizer element and down.  *
# Exactly one SldRasterSymbolizer is required.  * Bands may be selected by
# their proper EarthEngine names or   using numeric identifiers ("1", "2",
# ...). Proper   EarthEngine names are tried first.  * The Histogram and
# Normalize contrast stretch mechanisms are   supported.  * The
# type="values", type="intervals" and type="ramp"   attributes for ColorMap
# element in SLD 1.0 (GeoServer   extensions) are    supported.  * Opacity is
# only taken into account when it is 0.0   (transparent). Non-zero opacity
# values are treated as   completely opaque.  * The OverlapBehavior
# definition is currently ignored.  * The ShadedRelief mechanism is not
# currently supported.  * The ImageOutline mechanism is not currently
# supported.  * The Geometry element is ignored.  The output image will have
# histogram_bandname metadata if histogram equalization or normalization is
# requested.
#
# Args:
#   input: The image to rendering using the SLD.
#   sldXml: The OGC SLD 1.0 or 1.1 document (or fragment).
signatures.append({'args': [{'description': 'The image to rendering using the SLD.', 'name': 'input', 'type': 'Image'}, {'description': 'The OGC SLD 1.0 or 1.1 document (or fragment).', 'name': 'sldXml', 'type': 'String'}], 'description': 'Styles a raster input with the provided OGC SLD styling.\n\nPoints of note:\n * OGC SLD 1.0 and OGC SE 1.1 are supported.\n * The XML document passed in can be complete, or just the   SldRasterSymbolizer element and down.\n * Exactly one SldRasterSymbolizer is required.\n * Bands may be selected by their proper EarthEngine names or   using numeric identifiers ("1", "2", ...). Proper   EarthEngine names are tried first.\n * The Histogram and Normalize contrast stretch mechanisms are   supported.\n * The type="values", type="intervals" and type="ramp"   attributes for ColorMap element in SLD 1.0 (GeoServer   extensions) are\n   supported.\n * Opacity is only taken into account when it is 0.0   (transparent). Non-zero opacity values are treated as   completely opaque.\n * The OverlapBehavior definition is currently ignored.\n * The ShadedRelief mechanism is not currently supported.\n * The ImageOutline mechanism is not currently supported.\n * The Geometry element is ignored.\n\nThe output image will have histogram_bandname metadata if histogram equalization or normalization is requested.\n', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.sldStyle'})
# Image.slice
# Selects a contiguous group of bands from an image by position.
#
# Args:
#   image: The image from which to select bands.
#   start: Where to start the selection.  Negative numbers select
#       from the end, counting backwards.
#   end: Where to end the selection.  If omitted, selects all bands
#       from the start position to the end.
signatures.append({'args': [{'description': 'The image from which to select bands.', 'name': 'image', 'type': 'Image'}, {'description': 'Where to start the selection.  Negative numbers select from the end, counting backwards.', 'name': 'start', 'type': 'Integer'}, {'default': None, 'description': 'Where to end the selection.  If omitted, selects all bands from the start position to the end.', 'name': 'end', 'optional': True, 'type': 'Integer'}], 'description': 'Selects a contiguous group of bands from an image by position.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.slice'})
# Image.spectralDilation
# Computes the spectral/spatial dilation of an image by computing the
# spectral distance of each pixel under a structuring kernel from the
# centroid of all pixels under the kernel and taking the most distant result.
# See 'Spatial/spectral endmember extraction by multidimensional
# morphological operations.' IEEE transactions on geoscience and remote
# sensing 40.9 (2002): 2025-2041.
#
# Args:
#   image: The input image.
#   metric: The spectral distance metric to use.  One of  'sam'
#       (spectral angle mapper), 'sid' (spectral information
#       divergence),  'sed' (squared euclidean distance), or 'emd'
#       (earth movers distance).
#   kernel: Connectedness kernel.  Defaults to a square of radius 1
#       (8-way connected).
#   useCentroid: If true, distances are computed from the mean
#       of all pixels under the kernel instead of the kernel's
#       center pixel.
signatures.append({'args': [{'description': 'The input image.', 'name': 'image', 'type': 'Image'}, {'default': 'sam', 'description': "The spectral distance metric to use.  One of  'sam' (spectral angle mapper), 'sid' (spectral information divergence),  'sed' (squared euclidean distance), or 'emd' (earth movers distance).", 'name': 'metric', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'Connectedness kernel.  Defaults to a square of radius 1 (8-way connected).', 'name': 'kernel', 'optional': True, 'type': 'Kernel'}, {'default': False, 'description': "If true, distances are computed from the mean of all pixels under the kernel instead of the kernel's center pixel.", 'name': 'useCentroid', 'optional': True, 'type': 'Boolean'}], 'description': "Computes the spectral/spatial dilation of an image by computing the spectral distance of each pixel under a structuring kernel from the centroid of all pixels under the kernel and taking the most distant result. See 'Spatial/spectral endmember extraction by multidimensional morphological operations.' IEEE transactions on geoscience and remote sensing 40.9 (2002): 2025-2041.\n", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.spectralDilation'})
# Image.spectralDistance
# Computes the per-pixel spectral distance between two images.  If the images
# are array based then only the first band of each image is used; otherwise
# all bands are involved in the distance computation.  The two images are
# therefore expected  to contain the same number of bands or have the same
# 1-dimensional array length.
#
# Args:
#   image1: The first image.
#   image2: The second image.
#   metric: The spectral distance metric to use.  One of  'sam'
#       (spectral angle mapper), 'sid' (spectral information
#       divergence),  'sed' (squared euclidean distance), or 'emd'
#       (earth movers distance).
signatures.append({'args': [{'description': 'The first image.', 'name': 'image1', 'type': 'Image'}, {'description': 'The second image.', 'name': 'image2', 'type': 'Image'}, {'default': 'sam', 'description': "The spectral distance metric to use.  One of  'sam' (spectral angle mapper), 'sid' (spectral information divergence),  'sed' (squared euclidean distance), or 'emd' (earth movers distance).", 'name': 'metric', 'optional': True, 'type': 'String'}], 'description': 'Computes the per-pixel spectral distance between two images.  If the images are array based then only the first band of each image is used; otherwise all bands are involved in the distance computation.  The two images are therefore expected  to contain the same number of bands or have the same 1-dimensional array length.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.spectralDistance'})
# Image.spectralErosion
# Computes the spectral/spatial erosion of an image by computing the spectral
# distance of each pixel under a structuring kernel from the centroid of all
# pixels under the kernel and taking the closest result.  See
# 'Spatial/spectral endmember extraction by multidimensional morphological
# operations.' IEEE transactions on geoscience and remote sensing 40.9
# (2002): 2025-2041.
#
# Args:
#   image: The input image.
#   metric: The spectral distance metric to use.  One of  'sam'
#       (spectral angle mapper), 'sid' (spectral information
#       divergence),  'sed' (squared euclidean distance), or 'emd'
#       (earth movers distance).
#   kernel: Connectedness kernel.  Defaults to a square of radius 1
#       (8-way connected).
#   useCentroid: If true, distances are computed from the mean
#       of all pixels under the kernel instead of the kernel's
#       center pixel.
signatures.append({'args': [{'description': 'The input image.', 'name': 'image', 'type': 'Image'}, {'default': 'sam', 'description': "The spectral distance metric to use.  One of  'sam' (spectral angle mapper), 'sid' (spectral information divergence),  'sed' (squared euclidean distance), or 'emd' (earth movers distance).", 'name': 'metric', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'Connectedness kernel.  Defaults to a square of radius 1 (8-way connected).', 'name': 'kernel', 'optional': True, 'type': 'Kernel'}, {'default': False, 'description': "If true, distances are computed from the mean of all pixels under the kernel instead of the kernel's center pixel.", 'name': 'useCentroid', 'optional': True, 'type': 'Boolean'}], 'description': "Computes the spectral/spatial erosion of an image by computing the spectral distance of each pixel under a structuring kernel from the centroid of all pixels under the kernel and taking the closest result.  See 'Spatial/spectral endmember extraction by multidimensional morphological operations.' IEEE transactions on geoscience and remote sensing 40.9 (2002): 2025-2041.\n", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.spectralErosion'})
# Image.spectralGradient
# Computes the spectral gradient over all bands of an image (or the first
# band if the image is Array typed) by computing the per-pixel difference
# between the spectral erosion and dilation with a given structuring kernel
# and distance metric. See: Plaza, Antonio, et al. 'Spatial/spectral
# endmember extraction by multidimensional morphological operations.' IEEE
# transactions on geoscience and remote sensing 40.9 (2002): 2025-2041.
#
# Args:
#   image: The input image.
#   metric: The spectral distance metric to use.  One of  'sam'
#       (spectral angle mapper), 'sid' (spectral information
#       divergence),  'sed' (squared euclidean distance), or 'emd'
#       (earth movers distance).
#   kernel: Connectedness kernel.  Defaults to a square of radius 1
#       (8-way connected).
#   useCentroid: If true, distances are computed from the mean
#       of all pixels under the kernel instead of the kernel's
#       center pixel.
signatures.append({'args': [{'description': 'The input image.', 'name': 'image', 'type': 'Image'}, {'default': 'sam', 'description': "The spectral distance metric to use.  One of  'sam' (spectral angle mapper), 'sid' (spectral information divergence),  'sed' (squared euclidean distance), or 'emd' (earth movers distance).", 'name': 'metric', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'Connectedness kernel.  Defaults to a square of radius 1 (8-way connected).', 'name': 'kernel', 'optional': True, 'type': 'Kernel'}, {'default': False, 'description': "If true, distances are computed from the mean of all pixels under the kernel instead of the kernel's center pixel.", 'name': 'useCentroid', 'optional': True, 'type': 'Boolean'}], 'description': "Computes the spectral gradient over all bands of an image (or the first band if the image is Array typed) by computing the per-pixel difference between the spectral erosion and dilation with a given structuring kernel and distance metric. See: Plaza, Antonio, et al. 'Spatial/spectral endmember extraction by multidimensional morphological operations.' IEEE transactions on geoscience and remote sensing 40.9 (2002): 2025-2041.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.spectralGradient'})
# Image.sqrt
# Computes the square root of the input.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Computes the square root of the input.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.sqrt'})
# Image.stratifiedSample
# Extracts a stratified random sample of points from an image.  Extracts the
# specified number of samples for each distinct value discovered within the
# 'classBand'.  Returns a FeatureCollection of 1 Feature per extracted point,
# with each feature having 1 property per band in the input image.  If there
# are less than the specified number of samples available for a given class
# value, then all of the points for that class will be included.  Requires
# that the classBand contain integer values.
#
# Args:
#   image: The image to sample.
#   numPoints: The default number of points to sample in each
#       class.  Can be overridden for specific classes using the
#       'classValues' and 'classPoints' properties.
#   classBand: The name of the band containing the classes to
#       use for stratification. If unspecified, the first band
#       of the input image is used.
#   region: The region to sample from. If unspecified, the input
#       image's whole footprint is used.
#   scale: A nominal scale in meters of the projection to sample in.
#       Defaults to the scale of the first band of the input image.
#   projection: The projection in which to sample. If
#       unspecified, the projection of the input image's first
#       band is used. If specified in addition to scale,
#       rescaled to the specified scale.
#   seed: A randomization seed to use for subsampling.
#   classValues: A list of class values for which to override
#       the numPixels parameter. Must be the same size as
#       classPoints or null.
#   classPoints: A list of the per-class maximum number of
#       pixels to sample for each class in  the classValues
#       list.  Must be the same size as classValues or null.
#   dropNulls: Skip pixels in which any band is masked.
#   tileScale: A scaling factor used to reduce aggregation tile
#       size; using a larger tileScale (e.g. 2 or 4) may enable
#       computations that run out of memory with the default.
#   geometries: If true, the results will include a geometry
#       per sampled pixel.  Otherwise, geometries will be
#       omitted (saving memory).
signatures.append({'args': [{'description': 'The image to sample.', 'name': 'image', 'type': 'Image'}, {'description': "The default number of points to sample in each class.  Can be overridden for specific classes using the 'classValues' and 'classPoints' properties.", 'name': 'numPoints', 'type': 'Integer'}, {'default': None, 'description': 'The name of the band containing the classes to use for stratification. If unspecified, the first band of the input image is used.', 'name': 'classBand', 'optional': True, 'type': 'String'}, {'default': None, 'description': "The region to sample from. If unspecified, the input image's whole footprint is used.", 'name': 'region', 'optional': True, 'type': 'Geometry'}, {'default': None, 'description': 'A nominal scale in meters of the projection to sample in.  Defaults to the scale of the first band of the input image.', 'name': 'scale', 'optional': True, 'type': 'Float'}, {'default': None, 'description': "The projection in which to sample. If unspecified, the projection of the input image's first band is used. If specified in addition to scale, rescaled to the specified scale.", 'name': 'projection', 'optional': True, 'type': 'Projection'}, {'default': 0, 'description': 'A randomization seed to use for subsampling.', 'name': 'seed', 'optional': True, 'type': 'Integer'}, {'default': None, 'description': 'A list of class values for which to override the numPixels parameter. Must be the same size as classPoints or null.', 'name': 'classValues', 'optional': True, 'type': 'List'}, {'default': None, 'description': 'A list of the per-class maximum number of pixels to sample for each class in  the classValues list.  Must be the same size as classValues or null.', 'name': 'classPoints', 'optional': True, 'type': 'List'}, {'default': True, 'description': 'Skip pixels in which any band is masked.', 'name': 'dropNulls', 'optional': True, 'type': 'Boolean'}, {'default': 1.0, 'description': 'A scaling factor used to reduce aggregation tile size; using a larger tileScale (e.g. 2 or 4) may enable computations that run out of memory with the default.', 'name': 'tileScale', 'optional': True, 'type': 'Float'}, {'default': False, 'description': 'If true, the results will include a geometry per sampled pixel.  Otherwise, geometries will be omitted (saving memory).', 'name': 'geometries', 'optional': True, 'type': 'Boolean'}], 'description': "Extracts a stratified random sample of points from an image.  Extracts the specified number of samples for each distinct value discovered within the 'classBand'.  Returns a FeatureCollection of 1 Feature per extracted point, with each feature having 1 property per band in the input image.  If there are less than the specified number of samples available for a given class value, then all of the points for that class will be included.  Requires that the classBand contain integer values.", 'returns': 'FeatureCollection', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.stratifiedSample'})
# Image.subtract
# Subtracts the second value from the first for each matched pair of bands in
# image1 and image2. If either image1 or image2 has only 1 band, then it is
# used against all the bands in the other image. If the images have the same
# number of bands, but not the same names, they're used pairwise in the
# natural order. The output bands are named for the longer of the two inputs,
# or if they're equal in length, in image1's order. The type of the output
# pixels is the union of the input types.
#
# Args:
#   image1: The image from which the left operand bands are taken.
#   image2: The image from which the right operand bands are taken.
signatures.append({'args': [{'description': 'The image from which the left operand bands are taken.', 'name': 'image1', 'type': 'Image'}, {'description': 'The image from which the right operand bands are taken.', 'name': 'image2', 'type': 'Image'}], 'description': "Subtracts the second value from the first for each matched pair of bands in image1 and image2. If either image1 or image2 has only 1 band, then it is used against all the bands in the other image. If the images have the same number of bands, but not the same names, they're used pairwise in the natural order. The output bands are named for the longer of the two inputs, or if they're equal in length, in image1's order. The type of the output pixels is the union of the input types.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.subtract'})
# Image.tan
# Computes the tangent of the input in radians.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Computes the tangent of the input in radians.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.tan'})
# Image.tanh
# Computes the hyperbolic tangent of the input.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Computes the hyperbolic tangent of the input.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.tanh'})
# Image.toArray
# Concatenates pixels from each band into a single array per pixel. The
# result will be masked if any input bands are masked.
#
# Args:
#   image: Image of bands to convert to an array per pixel. Bands
#       must have scalar pixels, or array pixels with equal
#       dimensionality.
#   axis: Axis to concatenate along; must be at least 0 and at most
#       the dimension of the inputs. If the axis equals the dimension
#       of the inputs, the result will have 1 more dimension than the
#       inputs.
signatures.append({'args': [{'description': 'Image of bands to convert to an array per pixel. Bands must have scalar pixels, or array pixels with equal dimensionality.', 'name': 'image', 'type': 'Image'}, {'default': 0, 'description': 'Axis to concatenate along; must be at least 0 and at most the dimension of the inputs. If the axis equals the dimension of the inputs, the result will have 1 more dimension than the inputs.', 'name': 'axis', 'optional': True, 'type': 'Integer'}], 'description': 'Concatenates pixels from each band into a single array per pixel. The result will be masked if any input bands are masked.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.toArray'})
# Image.toByte
# Casts the input value to an unsigned 8-bit integer.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Casts the input value to an unsigned 8-bit integer.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.toByte'})
# Image.toDouble
# Casts the input value to a 64-bit float.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Casts the input value to a 64-bit float.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.toDouble'})
# Image.toFloat
# Casts the input value to a 32-bit float.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Casts the input value to a 32-bit float.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.toFloat'})
# Image.toInt
# Casts the input value to a signed 32-bit integer.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Casts the input value to a signed 32-bit integer.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.toInt'})
# Image.toInt16
# Casts the input value to a signed 16-bit integer.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Casts the input value to a signed 16-bit integer.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.toInt16'})
# Image.toInt32
# Casts the input value to a signed 32-bit integer.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Casts the input value to a signed 32-bit integer.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.toInt32'})
# Image.toInt64
# Casts the input value to a signed 64-bit integer.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Casts the input value to a signed 64-bit integer.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.toInt64'})
# Image.toInt8
# Casts the input value to a signed 8-bit integer.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Casts the input value to a signed 8-bit integer.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.toInt8'})
# Image.toLong
# Casts the input value to a signed 64-bit integer.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Casts the input value to a signed 64-bit integer.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.toLong'})
# Image.toShort
# Casts the input value to a signed 16-bit integer.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Casts the input value to a signed 16-bit integer.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.toShort'})
# Image.toUint16
# Casts the input value to an unsigned 16-bit integer.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Casts the input value to an unsigned 16-bit integer.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.toUint16'})
# Image.toUint32
# Casts the input value to an unsigned 32-bit integer.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Casts the input value to an unsigned 32-bit integer.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.toUint32'})
# Image.toUint8
# Casts the input value to an unsigned 8-bit integer.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Casts the input value to an unsigned 8-bit integer.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.toUint8'})
# Image.trainClassifier
# Trains an image classifier.  The input data is specified with the image and
# bands arguments.  To use a raster as training data, specify training_image,
# training_band, and training_region. The region is optional if the band is
# bounded. To use vector training data, specify training_features and
# training_property. The property defaults to 'classification'. You must
# specify either raster or vector training data, but not both.  The training
# data will be rasterized in a projection configured by the crs and
# crs_transform arguments. By default the projection of your training data
# will be used (if applicable); otherwise the projection of your input data.
# To use the classifier library, specify the classifier_name,
# classifier_parameters, and classifier_mode arguments.  To enable cross-
# validation or bagging, set the num_subsamples argument. When bagging, set
# the bootstrap_subsampling factor and the bootstrap_aggregator as well.  To
# use a custom classifier, specify it using the classifier parameter.
#
# Args:
#   image: The input data.
#   bands: The names of the bands from the image argument to train
#       on.
#   training_image: The pre-classified image for supervised
#       training. If specified, training_band must be
#       specified. Either this or training_features must be
#       specified.
#   training_band: The name of the band in training_image to
#       use. Ignored if training_image is not used.
#   training_region: The region of the training band to
#       use for training. If not specified, the whole band
#       is used. Ignored if training_image is not used.
#   training_features: A collection of classified
#       features to use for supervised classification.
#       Either this or training_image must be specified.
#   training_property: The name of the property in each
#       element of training_features containing its
#       class number.
#   crs: The ID of the coordinate reference system into which the
#       training data will be rasterized. If not specified, the
#       projection of the training data is used. If not applicable,
#       the projection of the input data. If this is specified,
#       crs_transform must be specified too.
#   crs_transform: The 6-element CRS transform matrix in the
#       order: xScale, yShearing, xShearing, yScale,
#       xTranslation and yTranslation. If crs is specified,
#       this must be specified.
#   max_classification: The maximum class number.
#       Deprecated and unused.
#   subsampling: Random sample the training raster by this
#       factor. Ignored if a classifier argument is provided.
#   seed: The random seed used for subsampling.
#   classifier_name: The name of the Abe classifier to
#       use. Currently supported values are
#       FastNaiveBayes, GmoMaxEnt, Winnow,
#       MultiClassPerceptron, Pegasos, Cart,
#       RifleSerialClassifier, IKPamir, VotingSvm,
#       MarginSvm, ContinuousNaiveBayes. Ignored if a
#       classifier argument is provided.
#   classifier_parameters: The Abe classifier
#       parameters. Ignored if a classifier argument
#       is provided.
#   classifier_mode: The classifier mode. Accepted values
#       are 'classification', 'regression' and
#       'probability'. Ignored if a classifier argument is
#       provided.
#   num_subsamples: The number of subsamples to use for
#       cross-validation or bagging. If 1, no cross-
#       validation or bagging is performed. Ignored if a
#       classifier argument is provided.
#   bootstrap_subsampling: The bootstrap subsampling
#       factor. Ignored if a classifier argument is
#       provided.
#   bootstrap_aggregator: The bootstrap aggregator.
#       Ignored if a classifier argument is provided.
#   classifier: A pre-built classifier to use.
signatures.append({'args': [{'description': 'The input data.', 'name': 'image', 'type': 'Image'}, {'default': None, 'description': 'The names of the bands from the image argument to train on.', 'name': 'bands', 'optional': True, 'type': 'List'}, {'default': None, 'description': 'The pre-classified image for supervised training. If specified, training_band must be specified. Either this or training_features must be specified.', 'name': 'training_image', 'optional': True, 'type': 'Image'}, {'default': None, 'description': 'The name of the band in training_image to use. Ignored if training_image is not used.', 'name': 'training_band', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The region of the training band to use for training. If not specified, the whole band is used. Ignored if training_image is not used.', 'name': 'training_region', 'optional': True, 'type': 'Geometry'}, {'default': None, 'description': 'A collection of classified features to use for supervised classification. Either this or training_image must be specified.', 'name': 'training_features', 'optional': True, 'type': 'FeatureCollection'}, {'default': 'classification', 'description': 'The name of the property in each element of training_features containing its class number.', 'name': 'training_property', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The ID of the coordinate reference system into which the training data will be rasterized. If not specified, the projection of the training data is used. If not applicable,  the projection of the input data. If this is specified, crs_transform must be specified too.', 'name': 'crs', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The 6-element CRS transform matrix in the order: xScale, yShearing, xShearing, yScale, xTranslation and yTranslation. If crs is specified, this must be specified.', 'name': 'crs_transform', 'optional': True, 'type': 'List'}, {'default': None, 'description': 'The maximum class number. Deprecated and unused.', 'name': 'max_classification', 'optional': True, 'type': 'Integer'}, {'default': 1.0, 'description': 'Random sample the training raster by this factor. Ignored if a classifier argument is provided.', 'name': 'subsampling', 'optional': True, 'type': 'Float'}, {'default': 0, 'description': 'The random seed used for subsampling.', 'name': 'seed', 'optional': True, 'type': 'Long'}, {'default': 'FastNaiveBayes', 'description': 'The name of the Abe classifier to use. Currently supported values are FastNaiveBayes, GmoMaxEnt, Winnow, MultiClassPerceptron, Pegasos, Cart, RifleSerialClassifier, IKPamir, VotingSvm, MarginSvm, ContinuousNaiveBayes. Ignored if a classifier argument is provided.', 'name': 'classifier_name', 'optional': True, 'type': 'String'}, {'default': '', 'description': 'The Abe classifier parameters. Ignored if a classifier argument is provided.', 'name': 'classifier_parameters', 'optional': True, 'type': 'String'}, {'default': 'classification', 'description': "The classifier mode. Accepted values are 'classification', 'regression' and 'probability'. Ignored if a classifier argument is provided.", 'name': 'classifier_mode', 'optional': True, 'type': 'String'}, {'default': 1, 'description': 'The number of subsamples to use for cross-validation or bagging. If 1, no cross-validation or bagging is performed. Ignored if a classifier argument is provided.', 'name': 'num_subsamples', 'optional': True, 'type': 'Integer'}, {'default': None, 'description': 'The bootstrap subsampling factor. Ignored if a classifier argument is provided.', 'name': 'bootstrap_subsampling', 'optional': True, 'type': 'Float'}, {'default': None, 'description': 'The bootstrap aggregator. Ignored if a classifier argument is provided.', 'name': 'bootstrap_aggregator', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'A pre-built classifier to use.', 'name': 'classifier', 'optional': True, 'type': 'OldClassifier'}], 'description': "Trains an image classifier.\n\nThe input data is specified with the image and bands arguments.\n\nTo use a raster as training data, specify training_image, training_band, and training_region. The region is optional if the band is bounded. To use vector training data, specify training_features and training_property. The property defaults to 'classification'. You must specify either raster or vector training data, but not both.\n\nThe training data will be rasterized in a projection configured by the crs and crs_transform arguments. By default the projection of your training data will be used (if applicable); otherwise the projection of your input data.\n\nTo use the classifier library, specify the classifier_name, classifier_parameters, and classifier_mode arguments.\n\nTo enable cross-validation or bagging, set the num_subsamples argument. When bagging, set the bootstrap_subsampling factor and the bootstrap_aggregator as well.\n\nTo use a custom classifier, specify it using the classifier parameter.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': True, 'deprecated': 'Use Classifier.train().', 'name': 'Image.trainClassifier'})
# Image.translate
# Translate the input image.
#
# Args:
#   input
#   x
#   y
#   units: The units for x and y; "meters" or "pixels".
#   proj: The projection in which to translate the image; defaults to
#       the projection of the first band.
signatures.append({'args': [{'name': 'input', 'type': 'Image'}, {'name': 'x', 'type': 'Float'}, {'name': 'y', 'type': 'Float'}, {'default': 'meters', 'description': 'The units for x and y; "meters" or "pixels".', 'name': 'units', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'The projection in which to translate the image; defaults to the projection of the first band.', 'name': 'proj', 'optional': True, 'type': 'Projection'}], 'description': 'Translate the input image.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.translate'})
# Image.trigamma
# Computes the trigamma function of the input.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Computes the trigamma function of the input.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.trigamma'})
# Image.uint16
# Casts the input value to an unsigned 16-bit integer.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Casts the input value to an unsigned 16-bit integer.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.uint16'})
# Image.uint32
# Casts the input value to an unsigned 32-bit integer.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Casts the input value to an unsigned 32-bit integer.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.uint32'})
# Image.uint8
# Casts the input value to an unsigned 8-bit integer.
#
# Args:
#   value: The image to which the operation is applied.
signatures.append({'args': [{'description': 'The image to which the operation is applied.', 'name': 'value', 'type': 'Image'}], 'description': 'Casts the input value to an unsigned 8-bit integer.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.uint8'})
# Image.unitScale
# Scales the input so that the range of input values [low, high] becomes [0,
# 1]. Values outside the range are NOT clamped. This algorithm always
# produces floating point pixels.
#
# Args:
#   input: The image to scale.
#   low: The value mapped to 0.
#   high: The value mapped to 1.
signatures.append({'args': [{'description': 'The image to scale.', 'name': 'input', 'type': 'Image'}, {'description': 'The value mapped to 0.', 'name': 'low', 'type': 'Float'}, {'description': 'The value mapped to 1.', 'name': 'high', 'type': 'Float'}], 'description': 'Scales the input so that the range of input values [low, high] becomes [0, 1]. Values outside the range are NOT clamped. This algorithm always produces floating point pixels.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.unitScale'})
# Image.unmask
# Replaces mask and value of the input image with the mask and value of
# another image at all positions where the input mask is zero. The output
# image retains the metadata of the input image. By default, the output image
# also retains the footprint of the input, but setting sameFootprint to false
# allows to extend the footprint.
#
# Args:
#   input: Input image.
#   value: New value and mask for the masked pixels of the input
#       image. If not specified, defaults to constant zero image
#       which is valid everywhere.
#   sameFootprint: If true (or unspecified), the output
#       retains the footprint of the input image. If false,
#       the footprint of the output is the union of the
#       input footprint with the footprint of the value
#       image.
signatures.append({'args': [{'description': 'Input image.', 'name': 'input', 'type': 'Image'}, {'default': None, 'description': 'New value and mask for the masked pixels of the input image. If not specified, defaults to constant zero image which is valid everywhere.', 'name': 'value', 'optional': True, 'type': 'Image'}, {'default': True, 'description': 'If true (or unspecified), the output retains the footprint of the input image. If false, the footprint of the output is the union of the input footprint with the footprint of the value image.', 'name': 'sameFootprint', 'optional': True, 'type': 'Boolean'}], 'description': 'Replaces mask and value of the input image with the mask and value of another image at all positions where the input mask is zero. The output image retains the metadata of the input image. By default, the output image also retains the footprint of the input, but setting sameFootprint to false allows to extend the footprint.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.unmask'})
# Image.unmix
# Unmix each pixel with the given endmembers, by computing the pseudo-inverse
# and multiplying it through each pixel.  Returns an image of doubles with
# the same number of bands as endmembers.
#
# Args:
#   image: The input image.
#   endmembers: The endmembers to unmix with.
#   sumToOne: Constrain the outputs to sum to one.
#   nonNegative: Constrain the outputs to be non-negative.
signatures.append({'args': [{'description': 'The input image.', 'name': 'image', 'type': 'Image'}, {'description': 'The endmembers to unmix with.', 'name': 'endmembers', 'type': 'List'}, {'default': False, 'description': 'Constrain the outputs to sum to one.', 'name': 'sumToOne', 'optional': True, 'type': 'Boolean'}, {'default': False, 'description': 'Constrain the outputs to be non-negative.', 'name': 'nonNegative', 'optional': True, 'type': 'Boolean'}], 'description': 'Unmix each pixel with the given endmembers, by computing the pseudo-inverse and multiplying it through each pixel.  Returns an image of doubles with the same number of bands as endmembers.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.unmix'})
# Image.updateMask
# Updates an image's mask at all positions where the existing mask is not
# zero. The output image retains the metadata and footprint of the input
# image.
#
# Args:
#   image: Input image.
#   mask: New mask for the image, as a floating-point value in the
#       range [0, 1] (invalid = 0, valid = 1). If this image has a
#       single band, it is used for all bands in the input image;
#       otherwise, must have the same number of bands as the input
#       image.
signatures.append({'args': [{'description': 'Input image.', 'name': 'image', 'type': 'Image'}, {'description': 'New mask for the image, as a floating-point value in the range [0, 1] (invalid = 0, valid = 1). If this image has a single band, it is used for all bands in the input image; otherwise, must have the same number of bands as the input image.', 'name': 'mask', 'type': 'Image'}], 'description': "Updates an image's mask at all positions where the existing mask is not zero. The output image retains the metadata and footprint of the input image.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.updateMask'})
# Image.visualize
# Produces an RGB or grayscale visualization of an image.  Each of the gain,
# bias, min, max and gamma arguments can take either a single value, which
# will be applied to all bands, or a list of values the same length as bands.
#
# Args:
#   image: The image to visualize.
#   bands: A list of the bands to visualize.  If empty, the first 3
#       are used.
#   gain: The visualization gain(s) to use.
#   bias: The visualization bias(es) to use.
#   min: The value(s) to map to RGB8 value 0.
#   max: The value(s) to map to RGB8 value 255.
#   gamma: The gamma correction factor(s) to use.
#   opacity: The opacity scaling factor to use.
#   palette: The color palette to use. List of CSS color
#       identifiers or hexadecimal color strings (e.g. ['red',
#       '00FF00', 'bluevlolet']).
#   forceRgbOutput: Whether to produce RGB output even for
#       single-band inputs.
signatures.append({'args': [{'description': 'The image to visualize.', 'name': 'image', 'type': 'Image'}, {'default': None, 'description': 'A list of the bands to visualize.  If empty, the first 3 are used.', 'name': 'bands', 'optional': True, 'type': 'Object'}, {'default': None, 'description': 'The visualization gain(s) to use.', 'name': 'gain', 'optional': True, 'type': 'Object'}, {'default': None, 'description': 'The visualization bias(es) to use.', 'name': 'bias', 'optional': True, 'type': 'Object'}, {'default': None, 'description': 'The value(s) to map to RGB8 value 0.', 'name': 'min', 'optional': True, 'type': 'Object'}, {'default': None, 'description': 'The value(s) to map to RGB8 value 255.', 'name': 'max', 'optional': True, 'type': 'Object'}, {'default': None, 'description': 'The gamma correction factor(s) to use.', 'name': 'gamma', 'optional': True, 'type': 'Object'}, {'default': None, 'description': 'The opacity scaling factor to use.', 'name': 'opacity', 'optional': True, 'type': 'Number'}, {'default': None, 'description': "The color palette to use. List of CSS color identifiers or hexadecimal color strings (e.g. ['red', '00FF00', 'bluevlolet']).", 'name': 'palette', 'optional': True, 'type': 'Object'}, {'default': False, 'description': 'Whether to produce RGB output even for single-band inputs.', 'name': 'forceRgbOutput', 'optional': True, 'type': 'Boolean'}], 'description': 'Produces an RGB or grayscale visualization of an image.  Each of the gain, bias, min, max and gamma arguments can take either a single value, which will be applied to all bands, or a list of values the same length as bands.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.visualize'})
# Image.where
# Performs conditional replacement of values.  For each pixel in each band of
# 'input', if the corresponding pixel in 'test' is nonzero, output the
# corresponding pixel in value, otherwise output the input pixel.  If at a
# given pixel, either test or value is masked, the input value is used. If
# the input is masked, nothing is done.  The output bands have the same names
# as the input bands. The output type of each band is the larger of the input
# and value types. The output image retains the metadata and footprint of the
# input image.
#
# Args:
#   input: The input image.
#   test: The test image. The pixels of this image determines which
#       of the input pixels is returned. If this is a single band, it
#       is used for all bands in the input image. This may not be an
#       array image.
#   value: The output value to use where test is not zero. If this
#       is a single band, it is used for all bands in the input
#       image.
signatures.append({'args': [{'description': 'The input image.', 'name': 'input', 'type': 'Image'}, {'description': 'The test image. The pixels of this image determines which of the input pixels is returned. If this is a single band, it is used for all bands in the input image. This may not be an array image.', 'name': 'test', 'type': 'Image'}, {'description': 'The output value to use where test is not zero. If this is a single band, it is used for all bands in the input image.', 'name': 'value', 'type': 'Image'}], 'description': "Performs conditional replacement of values.\n\nFor each pixel in each band of 'input', if the corresponding pixel in 'test' is nonzero, output the corresponding pixel in value, otherwise output the input pixel.\n\nIf at a given pixel, either test or value is masked, the input value is used. If the input is masked, nothing is done.\n\nThe output bands have the same names as the input bands. The output type of each band is the larger of the input and value types. The output image retains the metadata and footprint of the input image.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.where'})
# Image.zeroCrossing
# Finds zero-crossings on each band of an image.
#
# Args:
#   image: The image from which to compute zero crossings.
signatures.append({'args': [{'description': 'The image from which to compute zero crossings.', 'name': 'image', 'type': 'Image'}], 'description': 'Finds zero-crossings on each band of an image.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Image.zeroCrossing'})
# ImageCollection.cast
# Casts some or all bands of each image in an ImageCollection to the
# specified types.
#
# Args:
#   collection: The image collection to cast.
#   bandTypes: A dictionary from band name to band types. Types
#       can be PixelTypes or strings. The valid strings are:
#       'int8', 'int16', 'int32', 'int64', 'uint8', 'uint16',
#       'uint32', 'byte', 'short', 'int', 'long', 'float' and
#       'double'. Must include all bands already in any image in
#       the collection. If this includes bands that are not
#       already in an input image, they will be added to the
#       image as transparent bands.
#   bandOrder: A list specifying the order of the bands in the
#       result.Must match the keys of bandTypes.
signatures.append({'args': [{'description': 'The image collection to cast.', 'name': 'collection', 'type': 'ImageCollection'}, {'description': "A dictionary from band name to band types. Types can be PixelTypes or strings. The valid strings are: 'int8', 'int16', 'int32', 'int64', 'uint8', 'uint16', 'uint32', 'byte', 'short', 'int', 'long', 'float' and 'double'. Must include all bands already in any image in the collection. If this includes bands that are not already in an input image, they will be added to the image as transparent bands.", 'name': 'bandTypes', 'type': 'Dictionary'}, {'description': 'A list specifying the order of the bands in the result.Must match the keys of bandTypes.', 'name': 'bandOrder', 'type': 'List'}], 'description': 'Casts some or all bands of each image in an ImageCollection to the specified types.', 'returns': 'ImageCollection', 'type': 'Algorithm', 'hidden': False, 'name': 'ImageCollection.cast'})
# ImageCollection.combine
# Makes a new collection that is a copy of the images in primary, adding all
# the bands from the image in secondary with a matching ID. If there's no
# matching image, the primary image is just copied. This is equivalent to a
# join on ID with merging of the bands of the result.  Note that this
# algorithm assumes that for a matching pair of inputs, both have the same
# footprint and metadata.
#
# Args:
#   primary: The primary collection to join.
#   secondary: The secondary collection to join.
#   overwrite: If true, bands with the same name will get
#       overwritten. If false, bands with the same name will be
#       renamed.
signatures.append({'args': [{'description': 'The primary collection to join.', 'name': 'primary', 'type': 'ImageCollection'}, {'description': 'The secondary collection to join.', 'name': 'secondary', 'type': 'ImageCollection'}, {'default': False, 'description': 'If true, bands with the same name will get overwritten. If false, bands with the same name will be renamed.', 'name': 'overwrite', 'optional': True, 'type': 'Boolean'}], 'description': "Makes a new collection that is a copy of the images in primary, adding all the bands from the image in secondary with a matching ID. If there's no matching image, the primary image is just copied. This is equivalent to a join on ID with merging of the bands of the result.\n\nNote that this algorithm assumes that for a matching pair of inputs, both have the same footprint and metadata.", 'returns': 'ImageCollection', 'type': 'Algorithm', 'hidden': False, 'name': 'ImageCollection.combine'})
# ImageCollection.formaTrend
# Computes the long and short term trends of a time series or optionally, the
# trends of the ratio of the time series and a covariate.  The long term
# trend is estimated from the linear term of a regression on the full time
# series.  The short term trend is computed as the windowed minimum over the
# time series. The time series and covariate series are expected to contain a
# single band each, and the time series is expected to be evenly spaced in
# time.  The output is 4 float bands: the long and short term trends, the
# t-test of the long term trend against the time series, and the Bruce Hansen
# test of parameter stability.
#
# Args:
#   timeSeries: Collection from which to extract trends.
#   covariates: Cofactors to use in the trend analysis.
#   windowSize: Short term trend analysis window size, in
#       images.
signatures.append({'args': [{'description': 'Collection from which to extract trends.', 'name': 'timeSeries', 'type': 'ImageCollection'}, {'default': None, 'description': 'Cofactors to use in the trend analysis.', 'name': 'covariates', 'optional': True, 'type': 'ImageCollection'}, {'default': 6, 'description': 'Short term trend analysis window size, in images.', 'name': 'windowSize', 'optional': True, 'type': 'Integer'}], 'description': 'Computes the long and short term trends of a time series or optionally, the trends of the ratio of the time series and a covariate.  The long term trend is estimated from the linear term of a regression on the full time series.  The short term trend is computed as the windowed minimum over the time series.\nThe time series and covariate series are expected to contain a single band each, and the time series is expected to be evenly spaced in time.  The output is 4 float bands: the long and short term trends, the t-test of the long term trend against the time series, and the Bruce Hansen test of parameter stability.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'ImageCollection.formaTrend'})
# ImageCollection.fromImages
# Returns the image collection containing the given images.
#
# Args:
#   images: The images to include in the collection.
signatures.append({'args': [{'description': 'The images to include in the collection.', 'name': 'images', 'type': 'List'}], 'description': 'Returns the image collection containing the given images.', 'returns': 'ImageCollection', 'type': 'Algorithm', 'hidden': False, 'name': 'ImageCollection.fromImages'})
# ImageCollection.getRegion
# Output an array of values for each [pixel, band, image] tuple in an
# ImageCollection.  The output contains rows of id, lon, lat, time, and all
# bands for each image that intersects each pixel in the given region.
#
# Args:
#   collection: The image collection to extract data from.
#   geometry: The region over which to extract data.
#   scale: A nominal scale in meters of the projection to work in.
#   crs: The projection to work in. If unspecified, defaults to
#       EPSG:4326. If specified in addition to scale, the projection
#       is rescaled to the specified scale.
#   crsTransform: The array of CRS transform values.  This is
#       a row-major ordering of a 3x2 affine transform.  This
#       option is mutually exclusive with the scale option,
#       and will replace any transform already set on the
#       given projection.
signatures.append({'args': [{'description': 'The image collection to extract data from.', 'name': 'collection', 'type': 'ImageCollection'}, {'description': 'The region over which to extract data.', 'name': 'geometry', 'type': 'Geometry'}, {'default': None, 'description': 'A nominal scale in meters of the projection to work in.', 'name': 'scale', 'optional': True, 'type': 'Float'}, {'default': {'crs': 'EPSG:4326', 'transform': [1.0, 0.0, 0.0, 0.0, 1.0, 0.0], 'type': 'Projection'}, 'description': 'The projection to work in. If unspecified, defaults to EPSG:4326. If specified in addition to scale, the projection is rescaled to the specified scale.', 'name': 'crs', 'optional': True, 'type': 'Projection'}, {'default': None, 'description': 'The array of CRS transform values.  This is a row-major ordering of a 3x2 affine transform.  This option is mutually exclusive with the scale option, and will replace any transform already set on the given projection.', 'name': 'crsTransform', 'optional': True, 'type': 'List'}], 'description': 'Output an array of values for each [pixel, band, image] tuple in an ImageCollection.  The output contains rows of id, lon, lat, time, and all bands for each image that intersects each pixel in the given region.', 'returns': 'List', 'type': 'Algorithm', 'hidden': False, 'name': 'ImageCollection.getRegion'})
# ImageCollection.load
# Returns the image collection given its ID.
#
# Args:
#   id: The asset ID of the image collection.
#   version: The version of the asset. -1 signifies the latest
#       version.
signatures.append({'args': [{'description': 'The asset ID of the image collection.', 'name': 'id', 'type': 'String'}, {'default': None, 'description': 'The version of the asset. -1 signifies the latest version.', 'name': 'version', 'optional': True, 'type': 'Long'}], 'description': 'Returns the image collection given its ID.', 'returns': 'ImageCollection', 'type': 'Algorithm', 'hidden': False, 'name': 'ImageCollection.load'})
# ImageCollection.merge
# Merges two image collections into one. The result has all the images that
# were in either collection.
#
# Args:
#   collection1: The first collection to merge.
#   collection2: The second collection to merge.
signatures.append({'args': [{'description': 'The first collection to merge.', 'name': 'collection1', 'type': 'ImageCollection'}, {'description': 'The second collection to merge.', 'name': 'collection2', 'type': 'ImageCollection'}], 'description': 'Merges two image collections into one. The result has all the images that were in either collection.', 'returns': 'ImageCollection', 'type': 'Algorithm', 'hidden': False, 'name': 'ImageCollection.merge'})
# ImageCollection.mosaic
# Composites all the images in a collection, using the mask.
#
# Args:
#   collection: The collection to mosaic.
signatures.append({'args': [{'description': 'The collection to mosaic.', 'name': 'collection', 'type': 'ImageCollection'}], 'description': 'Composites all the images in a collection, using the mask.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'ImageCollection.mosaic'})
# ImageCollection.qualityMosaic
# Composites all the images in a collection, using a quality band as a per-
# pixel ordering function.
#
# Args:
#   collection: The collection to mosaic.
#   qualityBand: The name of the quality band in the
#       collection.
signatures.append({'args': [{'description': 'The collection to mosaic.', 'name': 'collection', 'type': 'ImageCollection'}, {'description': 'The name of the quality band in the collection.', 'name': 'qualityBand', 'type': 'String'}], 'description': 'Composites all the images in a collection, using a quality band as a per-pixel ordering function.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'ImageCollection.qualityMosaic'})
# ImageCollection.reduce
# Applies a reducer across all of the images in a collection. If the reducer
# has a single input, it will be applied separately to each band of the
# collection; otherwise it must have the same number of inputs as the
# collection has bands. The reducer output names determine the names of the
# output bands: reducers with multiple inputs will use the output names
# directly, while reducers with a single input will prefix the output name
# with the input band name (e.g. '10_mean', '20_mean', etc.).
#
# Args:
#   collection: The image collection to reduce.
#   reducer: The reducer to apply to the given collection.
#   parallelScale: A scaling factor used to limit memory
#       use; using a larger parallelScale (e.g. 2 or 4) may
#       enable computations that run out of memory with the
#       default.
signatures.append({'args': [{'description': 'The image collection to reduce.', 'name': 'collection', 'type': 'ImageCollection'}, {'description': 'The reducer to apply to the given collection.', 'name': 'reducer', 'type': 'Reducer'}, {'default': 1.0, 'description': 'A scaling factor used to limit memory use; using a larger parallelScale (e.g. 2 or 4) may enable computations that run out of memory with the default.', 'name': 'parallelScale', 'optional': True, 'type': 'Float'}], 'description': "Applies a reducer across all of the images in a collection.\nIf the reducer has a single input, it will be applied separately to each band of the collection; otherwise it must have the same number of inputs as the collection has bands.\nThe reducer output names determine the names of the output bands: reducers with multiple inputs will use the output names directly, while reducers with a single input will prefix the output name with the input band name (e.g. '10_mean', '20_mean', etc.).", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'ImageCollection.reduce'})
# ImageCollection.toArray
# Converts an image collection into an image of 2D arrays.  At each pixel,
# the images that have valid (unmasked) values in all bands are laid out
# along the first axis of the array in the order they appear in the image
# collection.  The bands of each image are laid out along the second axis of
# the array, in the order the bands appear in that image.  The array element
# type will be the union of the types of each band.
#
# Args:
#   collection: Image collection to convert to an array image.
#       Bands must have scalar values, not array values.
signatures.append({'args': [{'description': 'Image collection to convert to an array image. Bands must have scalar values, not array values.', 'name': 'collection', 'type': 'ImageCollection'}], 'description': 'Converts an image collection into an image of 2D arrays.  At each pixel, the images that have valid (unmasked) values in all bands are laid out along the first axis of the array in the order they appear in the image collection.  The bands of each image are laid out along the second axis of the array, in the order the bands appear in that image.  The array element type will be the union of the types of each band.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'ImageCollection.toArray'})
# ImageCollection.toArrayPerBand
# Concatenates multiple images into a single array image. The result will be
# masked if any input is masked.
#
# Args:
#   collection: Images to concatenate. A separate concatenation
#       is done per band, so all the images must have the same
#       dimensionality and shape per band, except length along
#       the concatenation axis.
#   axis: Axis to concatenate along; must be at least 0 and at most
#       the minimum dimension of any band in the collection.
signatures.append({'args': [{'description': 'Images to concatenate. A separate concatenation is done per band, so all the images must have the same dimensionality and shape per band, except length along the concatenation axis.', 'name': 'collection', 'type': 'ImageCollection'}, {'default': 0, 'description': 'Axis to concatenate along; must be at least 0 and at most the minimum dimension of any band in the collection.', 'name': 'axis', 'optional': True, 'type': 'Integer'}], 'description': 'Concatenates multiple images into a single array image. The result will be masked if any input is masked.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'ImageCollection.toArrayPerBand'})
# ImageCollection.toBands
# Converts a collection to a single multi-band image containing all of the
# bands of every image in the collection.  Output bands are named by
# prefixing the existing band names with the image id from which it came
# (e.g.: 'image1_band1')
#
# Args:
#   collection: The input collection.
signatures.append({'args': [{'description': 'The input collection.', 'name': 'collection', 'type': 'ImageCollection'}], 'description': "Converts a collection to a single multi-band image containing all of the bands of every image in the collection.  Output bands are named by prefixing the existing band names with the image id from which it came (e.g.: 'image1_band1')", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'ImageCollection.toBands'})
# IsEqual
# Returns whether two objects are equal.
#
# Args:
#   left
#   right
signatures.append({'args': [{'default': None, 'name': 'left', 'optional': True, 'type': 'Object'}, {'default': None, 'name': 'right', 'optional': True, 'type': 'Object'}], 'description': 'Returns whether two objects are equal.', 'returns': 'Boolean', 'type': 'Algorithm', 'hidden': False, 'name': 'IsEqual'})
# Join.apply
# Joins two collections.
#
# Args:
#   join: The join to apply; determines how the the results are
#       constructed.
#   primary: The primary collection.
#   secondary: The secondary collection.
#   condition: The join condition used to select the matches
#       from the two collections.
signatures.append({'args': [{'description': 'The join to apply; determines how the the results are constructed.', 'name': 'join', 'type': 'Join'}, {'description': 'The primary collection.', 'name': 'primary', 'type': 'FeatureCollection'}, {'description': 'The secondary collection.', 'name': 'secondary', 'type': 'FeatureCollection'}, {'description': 'The join condition used to select the matches from the two collections.', 'name': 'condition', 'type': 'Filter'}], 'description': 'Joins two collections.', 'returns': 'FeatureCollection', 'type': 'Algorithm', 'hidden': False, 'name': 'Join.apply'})
# Join.inner
# Returns a join that pairs elements from the primary collection with
# matching elements from the secondary collection. Each result has a
# 'primary' property that contains the element from the primary collection,
# and a 'secondary' property containing the matching element from the
# secondary collection. If measureKey is specified, the join measure is also
# attached to the object as a property.
#
# Args:
#   primaryKey: The property name used to save the primary
#       match.
#   secondaryKey: The property name used to save the
#       secondary match.
#   measureKey: An optional property name used to save the
#       measure of the join condition.
signatures.append({'args': [{'default': 'primary', 'description': 'The property name used to save the primary match.', 'name': 'primaryKey', 'optional': True, 'type': 'String'}, {'default': 'secondary', 'description': 'The property name used to save the secondary match.', 'name': 'secondaryKey', 'optional': True, 'type': 'String'}, {'default': None, 'description': 'An optional property name used to save the measure of the join condition.', 'name': 'measureKey', 'optional': True, 'type': 'String'}], 'description': "Returns a join that pairs elements from the primary collection with matching elements from the secondary collection. Each result has a 'primary' property that contains the element from the primary collection, and a 'secondary' property containing the matching element from the secondary collection. If measureKey is specified, the join measure is also attached to the object as a property.", 'returns': 'Join', 'type': 'Algorithm', 'hidden': False, 'name': 'Join.inner'})
# Join.inverted
# Returns a join that produces the elements of the primary collection that
# match no elements of the secondary collection. No properties are added to
# the results.
signatures.append({'args': [], 'description': 'Returns a join that produces the elements of the primary collection that match no elements of the secondary collection. No properties are added to the results.', 'returns': 'Join', 'type': 'Algorithm', 'hidden': False, 'name': 'Join.inverted'})
# Join.saveAll
# Returns a join that pairs each element from the first collection with a
# group of matching elements from the second collection. The list of matches
# is added to each result as an additional property. If measureKey is
# specified, each match has the value of its join measure attached. Join
# measures are produced when withinDistance or maxDifference filters are used
# as the join condition.
#
# Args:
#   matchesKey: The property name used to save the matches
#       list.
#   ordering: The property on which to sort the matches list.
#   ascending: Whether the ordering is ascending.
#   measureKey: An optional property name used to save the
#       measure of the join condition on each match.
signatures.append({'args': [{'description': 'The property name used to save the matches list.', 'name': 'matchesKey', 'type': 'String'}, {'default': None, 'description': 'The property on which to sort the matches list.', 'name': 'ordering', 'optional': True, 'type': 'String'}, {'default': True, 'description': 'Whether the ordering is ascending.', 'name': 'ascending', 'optional': True, 'type': 'Boolean'}, {'default': None, 'description': 'An optional property name used to save the measure of the join condition on each match.', 'name': 'measureKey', 'optional': True, 'type': 'String'}], 'description': 'Returns a join that pairs each element from the first collection with a group of matching elements from the second collection. The list of matches is added to each result as an additional property. If measureKey is specified, each match has the value of its join measure attached. Join measures are produced when withinDistance or maxDifference filters are used as the join condition.', 'returns': 'Join', 'type': 'Algorithm', 'hidden': False, 'name': 'Join.saveAll'})
# Join.saveBest
# Returns a join that pairs each element from the first collection with a
# matching element from the second collection. The match with the best join
# measure is added to each result as an additional property. Join measures
# are produced when withinDistance or maxDifference filters are used as the
# join condition.
#
# Args:
#   matchKey: The key used to save the match.
#   measureKey: The key used to save the measure of the join
#       condition on the match.
signatures.append({'args': [{'description': 'The key used to save the match.', 'name': 'matchKey', 'type': 'String'}, {'description': 'The key used to save the measure of the join condition on the match.', 'name': 'measureKey', 'type': 'String'}], 'description': 'Returns a join that pairs each element from the first collection with a matching element from the second collection. The match with the best join measure is added to each result as an additional property. Join measures are produced when withinDistance or maxDifference filters are used as the join condition.', 'returns': 'Join', 'type': 'Algorithm', 'hidden': False, 'name': 'Join.saveBest'})
# Join.saveFirst
# Returns a join that pairs each element from the first collection with a
# matching element from the second collection. The first match is added to
# the result as an additional property.
#
# Args:
#   matchKey: The property name used to save the match.
#   ordering: The property on which to sort the matches before
#       selecting the first.
#   ascending: Whether the ordering is ascending.
#   measureKey: An optional property name used to save the
#       measure of the join condition on the match.
signatures.append({'args': [{'description': 'The property name used to save the match.', 'name': 'matchKey', 'type': 'String'}, {'default': None, 'description': 'The property on which to sort the matches before selecting the first.', 'name': 'ordering', 'optional': True, 'type': 'String'}, {'default': True, 'description': 'Whether the ordering is ascending.', 'name': 'ascending', 'optional': True, 'type': 'Boolean'}, {'default': None, 'description': 'An optional property name used to save the measure of the join condition on the match.', 'name': 'measureKey', 'optional': True, 'type': 'String'}], 'description': 'Returns a join that pairs each element from the first collection with a matching element from the second collection. The first match is added to the result as an additional property.', 'returns': 'Join', 'type': 'Algorithm', 'hidden': False, 'name': 'Join.saveFirst'})
# Join.simple
# Returns a join that produces the elements of the primary collection that
# match any element of the secondary collection. No properties are added to
# the results.
signatures.append({'args': [], 'description': 'Returns a join that produces the elements of the primary collection that match any element of the secondary collection. No properties are added to the results.', 'returns': 'Join', 'type': 'Algorithm', 'hidden': False, 'name': 'Join.simple'})
# Kernel.add
# Adds two kernels (pointwise), after aligning their centers.
#
# Args:
#   kernel1: The first kernel.
#   kernel2: The second kernel.
#   normalize: Normalize the kernel.
signatures.append({'args': [{'description': 'The first kernel.', 'name': 'kernel1', 'type': 'Kernel'}, {'description': 'The second kernel.', 'name': 'kernel2', 'type': 'Kernel'}, {'default': False, 'description': 'Normalize the kernel.', 'name': 'normalize', 'optional': True, 'type': 'Boolean'}], 'description': 'Adds two kernels (pointwise), after aligning their centers.', 'returns': 'Kernel', 'type': 'Algorithm', 'hidden': False, 'name': 'Kernel.add'})
# Kernel.chebyshev
# Generates a distance kernel based on Chebyshev distance (greatest distance
# along any dimension).
#
# Args:
#   radius: The radius of the kernel to generate.
#   units: The system of measurement for the kernel ('pixels' or
#       'meters'). If the kernel is specified in meters, it will
#       resize when the zoom-level is changed.
#   normalize: Normalize the kernel values to sum to 1.
#   magnitude: Scale each value by this amount.
signatures.append({'args': [{'description': 'The radius of the kernel to generate.', 'name': 'radius', 'type': 'Float'}, {'default': 'pixels', 'description': "The system of measurement for the kernel ('pixels' or 'meters'). If the kernel is specified in meters, it will resize when the zoom-level is changed.", 'name': 'units', 'optional': True, 'type': 'String'}, {'default': False, 'description': 'Normalize the kernel values to sum to 1.', 'name': 'normalize', 'optional': True, 'type': 'Boolean'}, {'default': 1.0, 'description': 'Scale each value by this amount.', 'name': 'magnitude', 'optional': True, 'type': 'Float'}], 'description': 'Generates a distance kernel based on Chebyshev distance (greatest distance along any dimension).', 'returns': 'Kernel', 'type': 'Algorithm', 'hidden': False, 'name': 'Kernel.chebyshev'})
# Kernel.circle
# Generates a circle-shaped boolean kernel.
#
# Args:
#   radius: The radius of the kernel to generate.
#   units: The system of measurement for the kernel ('pixels' or
#       'meters'). If the kernel is specified in meters, it will
#       resize when the zoom-level is changed.
#   normalize: Normalize the kernel values to sum to 1.
#   magnitude: Scale each value by this amount.
signatures.append({'args': [{'description': 'The radius of the kernel to generate.', 'name': 'radius', 'type': 'Float'}, {'default': 'pixels', 'description': "The system of measurement for the kernel ('pixels' or 'meters'). If the kernel is specified in meters, it will resize when the zoom-level is changed.", 'name': 'units', 'optional': True, 'type': 'String'}, {'default': True, 'description': 'Normalize the kernel values to sum to 1.', 'name': 'normalize', 'optional': True, 'type': 'Boolean'}, {'default': 1.0, 'description': 'Scale each value by this amount.', 'name': 'magnitude', 'optional': True, 'type': 'Float'}], 'description': 'Generates a circle-shaped boolean kernel.', 'returns': 'Kernel', 'type': 'Algorithm', 'hidden': False, 'name': 'Kernel.circle'})
# Kernel.compass
# Generates a 3x3 Prewitt's Compass edge-detection kernel.
#
# Args:
#   magnitude: Scale each value by this amount.
#   normalize: Normalize the kernel values to sum to 1.
signatures.append({'args': [{'default': 1.0, 'description': 'Scale each value by this amount.', 'name': 'magnitude', 'optional': True, 'type': 'Float'}, {'default': False, 'description': 'Normalize the kernel values to sum to 1.', 'name': 'normalize', 'optional': True, 'type': 'Boolean'}], 'description': "Generates a 3x3 Prewitt's Compass edge-detection kernel.", 'returns': 'Kernel', 'type': 'Algorithm', 'hidden': False, 'name': 'Kernel.compass'})
# Kernel.cross
# Generates a cross-shaped boolean kernel.
#
# Args:
#   radius: The radius of the kernel to generate.
#   units: The system of measurement for the kernel ('pixels' or
#       'meters'). If the kernel is specified in meters, it will
#       resize when the zoom-level is changed.
#   normalize: Normalize the kernel values to sum to 1.
#   magnitude: Scale each value by this amount.
signatures.append({'args': [{'description': 'The radius of the kernel to generate.', 'name': 'radius', 'type': 'Float'}, {'default': 'pixels', 'description': "The system of measurement for the kernel ('pixels' or 'meters'). If the kernel is specified in meters, it will resize when the zoom-level is changed.", 'name': 'units', 'optional': True, 'type': 'String'}, {'default': True, 'description': 'Normalize the kernel values to sum to 1.', 'name': 'normalize', 'optional': True, 'type': 'Boolean'}, {'default': 1.0, 'description': 'Scale each value by this amount.', 'name': 'magnitude', 'optional': True, 'type': 'Float'}], 'description': 'Generates a cross-shaped boolean kernel.', 'returns': 'Kernel', 'type': 'Algorithm', 'hidden': False, 'name': 'Kernel.cross'})
# Kernel.diamond
# Generates a diamond-shaped boolean kernel.
#
# Args:
#   radius: The radius of the kernel to generate.
#   units: The system of measurement for the kernel ('pixels' or
#       'meters'). If the kernel is specified in meters, it will
#       resize when the zoom-level is changed.
#   normalize: Normalize the kernel values to sum to 1.
#   magnitude: Scale each value by this amount.
signatures.append({'args': [{'description': 'The radius of the kernel to generate.', 'name': 'radius', 'type': 'Float'}, {'default': 'pixels', 'description': "The system of measurement for the kernel ('pixels' or 'meters'). If the kernel is specified in meters, it will resize when the zoom-level is changed.", 'name': 'units', 'optional': True, 'type': 'String'}, {'default': True, 'description': 'Normalize the kernel values to sum to 1.', 'name': 'normalize', 'optional': True, 'type': 'Boolean'}, {'default': 1.0, 'description': 'Scale each value by this amount.', 'name': 'magnitude', 'optional': True, 'type': 'Float'}], 'description': 'Generates a diamond-shaped boolean kernel.', 'returns': 'Kernel', 'type': 'Algorithm', 'hidden': False, 'name': 'Kernel.diamond'})
# Kernel.euclidean
# Generates a distance kernel based on Euclidean (straight-line) distance.
#
# Args:
#   radius: The radius of the kernel to generate.
#   units: The system of measurement for the kernel ('pixels' or
#       'meters'). If the kernel is specified in meters, it will
#       resize when the zoom-level is changed.
#   normalize: Normalize the kernel values to sum to 1.
#   magnitude: Scale each value by this amount.
signatures.append({'args': [{'description': 'The radius of the kernel to generate.', 'name': 'radius', 'type': 'Float'}, {'default': 'pixels', 'description': "The system of measurement for the kernel ('pixels' or 'meters'). If the kernel is specified in meters, it will resize when the zoom-level is changed.", 'name': 'units', 'optional': True, 'type': 'String'}, {'default': False, 'description': 'Normalize the kernel values to sum to 1.', 'name': 'normalize', 'optional': True, 'type': 'Boolean'}, {'default': 1.0, 'description': 'Scale each value by this amount.', 'name': 'magnitude', 'optional': True, 'type': 'Float'}], 'description': 'Generates a distance kernel based on Euclidean (straight-line) distance.', 'returns': 'Kernel', 'type': 'Algorithm', 'hidden': False, 'name': 'Kernel.euclidean'})
# Kernel.fixed
# Creates a Kernel.
#
# Args:
#   width: The width of the kernel in pixels.
#   height: The height of the kernel in pixels.
#   weights: The pixel values of the kernel.
#   x: The location of the focus, as an offset from the left.
#   y: The location of the focus, as an offset from the top.
#   normalize: Normalize the kernel values to sum to 1.
signatures.append({'args': [{'default': -1, 'description': 'The width of the kernel in pixels.', 'name': 'width', 'optional': True, 'type': 'Integer'}, {'default': -1, 'description': 'The height of the kernel in pixels.', 'name': 'height', 'optional': True, 'type': 'Integer'}, {'description': 'The pixel values of the kernel.', 'name': 'weights', 'type': 'List'}, {'default': -1, 'description': 'The location of the focus, as an offset from the left.', 'name': 'x', 'optional': True, 'type': 'Integer'}, {'default': -1, 'description': 'The location of the focus, as an offset from the top.', 'name': 'y', 'optional': True, 'type': 'Integer'}, {'default': False, 'description': 'Normalize the kernel values to sum to 1.', 'name': 'normalize', 'optional': True, 'type': 'Boolean'}], 'description': 'Creates a Kernel.', 'returns': 'Kernel', 'type': 'Algorithm', 'hidden': False, 'name': 'Kernel.fixed'})
# Kernel.gaussian
# Generates a Gaussian kernel from a sampled continuous Gaussian.
#
# Args:
#   radius: The radius of the kernel to generate.
#   sigma: Standard deviation of the Gaussian function (same units
#       as radius).
#   units: The system of measurement for the kernel ('pixels' or
#       'meters'). If the kernel is specified in meters, it will
#       resize when the zoom-level is changed.
#   normalize: Normalize the kernel values to sum to 1.
#   magnitude: Scale each value by this amount.
signatures.append({'args': [{'description': 'The radius of the kernel to generate.', 'name': 'radius', 'type': 'Float'}, {'default': 1.0, 'description': 'Standard deviation of the Gaussian function (same units as radius).', 'name': 'sigma', 'optional': True, 'type': 'Float'}, {'default': 'pixels', 'description': "The system of measurement for the kernel ('pixels' or 'meters'). If the kernel is specified in meters, it will resize when the zoom-level is changed.", 'name': 'units', 'optional': True, 'type': 'String'}, {'default': True, 'description': 'Normalize the kernel values to sum to 1.', 'name': 'normalize', 'optional': True, 'type': 'Boolean'}, {'default': 1.0, 'description': 'Scale each value by this amount.', 'name': 'magnitude', 'optional': True, 'type': 'Float'}], 'description': 'Generates a Gaussian kernel from a sampled continuous Gaussian.', 'returns': 'Kernel', 'type': 'Algorithm', 'hidden': False, 'name': 'Kernel.gaussian'})
# Kernel.inverse
# Returns a kernel which has each of its weights multiplicatively inverted.
# Weights with a value of zero are not inverted and remain zero.
#
# Args:
#   kernel: The kernel to have its entries inverted.
signatures.append({'args': [{'description': 'The kernel to have its entries inverted.', 'name': 'kernel', 'type': 'Kernel'}], 'description': 'Returns a kernel which has each of its weights multiplicatively inverted. Weights with a value of zero are not inverted and remain zero.', 'returns': 'Kernel', 'type': 'Algorithm', 'hidden': False, 'name': 'Kernel.inverse'})
# Kernel.kirsch
# Generates a 3x3 Kirsch's Compass edge-detection kernel.
#
# Args:
#   magnitude: Scale each value by this amount.
#   normalize: Normalize the kernel values to sum to 1.
signatures.append({'args': [{'default': 1.0, 'description': 'Scale each value by this amount.', 'name': 'magnitude', 'optional': True, 'type': 'Float'}, {'default': False, 'description': 'Normalize the kernel values to sum to 1.', 'name': 'normalize', 'optional': True, 'type': 'Boolean'}], 'description': "Generates a 3x3 Kirsch's Compass edge-detection kernel.", 'returns': 'Kernel', 'type': 'Algorithm', 'hidden': False, 'name': 'Kernel.kirsch'})
# Kernel.laplacian4
# Generates a 3x3 Laplacian-4 edge-detection kernel.
#
# Args:
#   magnitude: Scale each value by this amount.
#   normalize: Normalize the kernel values to sum to 1.
signatures.append({'args': [{'default': 1.0, 'description': 'Scale each value by this amount.', 'name': 'magnitude', 'optional': True, 'type': 'Float'}, {'default': False, 'description': 'Normalize the kernel values to sum to 1.', 'name': 'normalize', 'optional': True, 'type': 'Boolean'}], 'description': 'Generates a 3x3 Laplacian-4 edge-detection kernel.', 'returns': 'Kernel', 'type': 'Algorithm', 'hidden': False, 'name': 'Kernel.laplacian4'})
# Kernel.laplacian8
# Generates a 3x3 Laplacian-8 edge-detection kernel.
#
# Args:
#   magnitude: Scale each value by this amount.
#   normalize: Normalize the kernel values to sum to 1.
signatures.append({'args': [{'default': 1.0, 'description': 'Scale each value by this amount.', 'name': 'magnitude', 'optional': True, 'type': 'Float'}, {'default': False, 'description': 'Normalize the kernel values to sum to 1.', 'name': 'normalize', 'optional': True, 'type': 'Boolean'}], 'description': 'Generates a 3x3 Laplacian-8 edge-detection kernel.', 'returns': 'Kernel', 'type': 'Algorithm', 'hidden': False, 'name': 'Kernel.laplacian8'})
# Kernel.manhattan
# Generates a distance kernel based on rectilinear (city-block) distance.
#
# Args:
#   radius: The radius of the kernel to generate.
#   units: The system of measurement for the kernel ('pixels' or
#       'meters'). If the kernel is specified in meters, it will
#       resize when the zoom-level is changed.
#   normalize: Normalize the kernel values to sum to 1.
#   magnitude: Scale each value by this amount.
signatures.append({'args': [{'description': 'The radius of the kernel to generate.', 'name': 'radius', 'type': 'Float'}, {'default': 'pixels', 'description': "The system of measurement for the kernel ('pixels' or 'meters'). If the kernel is specified in meters, it will resize when the zoom-level is changed.", 'name': 'units', 'optional': True, 'type': 'String'}, {'default': False, 'description': 'Normalize the kernel values to sum to 1.', 'name': 'normalize', 'optional': True, 'type': 'Boolean'}, {'default': 1.0, 'description': 'Scale each value by this amount.', 'name': 'magnitude', 'optional': True, 'type': 'Float'}], 'description': 'Generates a distance kernel based on rectilinear (city-block) distance.', 'returns': 'Kernel', 'type': 'Algorithm', 'hidden': False, 'name': 'Kernel.manhattan'})
# Kernel.octagon
# Generates an octagon-shaped boolean kernel.
#
# Args:
#   radius: The radius of the kernel to generate.
#   units: The system of measurement for the kernel ('pixels' or
#       'meters'). If the kernel is specified in meters, it will
#       resize when the zoom-level is changed.
#   normalize: Normalize the kernel values to sum to 1.
#   magnitude: Scale each value by this amount.
signatures.append({'args': [{'description': 'The radius of the kernel to generate.', 'name': 'radius', 'type': 'Float'}, {'default': 'pixels', 'description': "The system of measurement for the kernel ('pixels' or 'meters'). If the kernel is specified in meters, it will resize when the zoom-level is changed.", 'name': 'units', 'optional': True, 'type': 'String'}, {'default': True, 'description': 'Normalize the kernel values to sum to 1.', 'name': 'normalize', 'optional': True, 'type': 'Boolean'}, {'default': 1.0, 'description': 'Scale each value by this amount.', 'name': 'magnitude', 'optional': True, 'type': 'Float'}], 'description': 'Generates an octagon-shaped boolean kernel.', 'returns': 'Kernel', 'type': 'Algorithm', 'hidden': False, 'name': 'Kernel.octagon'})
# Kernel.plus
# Generates a plus-shaped boolean kernel.
#
# Args:
#   radius: The radius of the kernel to generate.
#   units: The system of measurement for the kernel ('pixels' or
#       'meters'). If the kernel is specified in meters, it will
#       resize when the zoom-level is changed.
#   normalize: Normalize the kernel values to sum to 1.
#   magnitude: Scale each value by this amount.
signatures.append({'args': [{'description': 'The radius of the kernel to generate.', 'name': 'radius', 'type': 'Float'}, {'default': 'pixels', 'description': "The system of measurement for the kernel ('pixels' or 'meters'). If the kernel is specified in meters, it will resize when the zoom-level is changed.", 'name': 'units', 'optional': True, 'type': 'String'}, {'default': True, 'description': 'Normalize the kernel values to sum to 1.', 'name': 'normalize', 'optional': True, 'type': 'Boolean'}, {'default': 1.0, 'description': 'Scale each value by this amount.', 'name': 'magnitude', 'optional': True, 'type': 'Float'}], 'description': 'Generates a plus-shaped boolean kernel.', 'returns': 'Kernel', 'type': 'Algorithm', 'hidden': False, 'name': 'Kernel.plus'})
# Kernel.prewitt
# Generates a 3x3 Prewitt edge-detection kernel.
#
# Args:
#   magnitude: Scale each value by this amount.
#   normalize: Normalize the kernel values to sum to 1.
signatures.append({'args': [{'default': 1.0, 'description': 'Scale each value by this amount.', 'name': 'magnitude', 'optional': True, 'type': 'Float'}, {'default': False, 'description': 'Normalize the kernel values to sum to 1.', 'name': 'normalize', 'optional': True, 'type': 'Boolean'}], 'description': 'Generates a 3x3 Prewitt edge-detection kernel.', 'returns': 'Kernel', 'type': 'Algorithm', 'hidden': False, 'name': 'Kernel.prewitt'})
# Kernel.rectangle
# Generates a rectangular-shaped kernel.
#
# Args:
#   xRadius: The horizontal radius of the kernel to generate.
#   yRadius: The vertical radius of the kernel to generate.
#   units: The system of measurement for the kernel ("pixels" or
#       "meters"). If the kernel is specified in meters, it will
#       resize when the zoom-level is changed.
#   normalize: Normalize the kernel values to sum to 1.
#   magnitude: Scale each value by this amount.
signatures.append({'args': [{'description': 'The horizontal radius of the kernel to generate.', 'name': 'xRadius', 'type': 'Float'}, {'description': 'The vertical radius of the kernel to generate.', 'name': 'yRadius', 'type': 'Float'}, {'default': 'pixels', 'description': 'The system of measurement for the kernel ("pixels" or "meters"). If the kernel is specified in meters, it will resize when the zoom-level is changed.', 'name': 'units', 'optional': True, 'type': 'String'}, {'default': True, 'description': 'Normalize the kernel values to sum to 1.', 'name': 'normalize', 'optional': True, 'type': 'Boolean'}, {'default': 1.0, 'description': 'Scale each value by this amount.', 'name': 'magnitude', 'optional': True, 'type': 'Float'}], 'description': 'Generates a rectangular-shaped kernel.', 'returns': 'Kernel', 'type': 'Algorithm', 'hidden': False, 'name': 'Kernel.rectangle'})
# Kernel.roberts
# Generates a 2x2 Roberts edge-detection kernel.
#
# Args:
#   magnitude: Scale each value by this amount.
#   normalize: Normalize the kernel values to sum to 1.
signatures.append({'args': [{'default': 1.0, 'description': 'Scale each value by this amount.', 'name': 'magnitude', 'optional': True, 'type': 'Float'}, {'default': False, 'description': 'Normalize the kernel values to sum to 1.', 'name': 'normalize', 'optional': True, 'type': 'Boolean'}], 'description': 'Generates a 2x2 Roberts edge-detection kernel.', 'returns': 'Kernel', 'type': 'Algorithm', 'hidden': False, 'name': 'Kernel.roberts'})
# Kernel.rotate
# Creates a Kernel.
#
# Args:
#   kernel: The kernel to be rotated.
#   rotations: Number of 90 deg. rotations to make (negative
#       numbers rotate counterclockwise).
signatures.append({'args': [{'description': 'The kernel to be rotated.', 'name': 'kernel', 'type': 'Kernel'}, {'description': 'Number of 90 deg. rotations to make (negative numbers rotate counterclockwise).', 'name': 'rotations', 'type': 'Integer'}], 'description': 'Creates a Kernel.', 'returns': 'Kernel', 'type': 'Algorithm', 'hidden': False, 'name': 'Kernel.rotate'})
# Kernel.sobel
# Generates a 3x3 Sobel edge-detection kernel.
#
# Args:
#   magnitude: Scale each value by this amount.
#   normalize: Normalize the kernel values to sum to 1.
signatures.append({'args': [{'default': 1.0, 'description': 'Scale each value by this amount.', 'name': 'magnitude', 'optional': True, 'type': 'Float'}, {'default': False, 'description': 'Normalize the kernel values to sum to 1.', 'name': 'normalize', 'optional': True, 'type': 'Boolean'}], 'description': 'Generates a 3x3 Sobel edge-detection kernel.', 'returns': 'Kernel', 'type': 'Algorithm', 'hidden': False, 'name': 'Kernel.sobel'})
# Kernel.square
# Generates a square-shaped boolean kernel.
#
# Args:
#   radius: The radius of the kernel to generate.
#   units: The system of measurement for the kernel ('pixels' or
#       'meters'). If the kernel is specified in meters, it will
#       resize when the zoom-level is changed.
#   normalize: Normalize the kernel values to sum to 1.
#   magnitude: Scale each value by this amount.
signatures.append({'args': [{'description': 'The radius of the kernel to generate.', 'name': 'radius', 'type': 'Float'}, {'default': 'pixels', 'description': "The system of measurement for the kernel ('pixels' or 'meters'). If the kernel is specified in meters, it will resize when the zoom-level is changed.", 'name': 'units', 'optional': True, 'type': 'String'}, {'default': True, 'description': 'Normalize the kernel values to sum to 1.', 'name': 'normalize', 'optional': True, 'type': 'Boolean'}, {'default': 1.0, 'description': 'Scale each value by this amount.', 'name': 'magnitude', 'optional': True, 'type': 'Float'}], 'description': 'Generates a square-shaped boolean kernel.', 'returns': 'Kernel', 'type': 'Algorithm', 'hidden': False, 'name': 'Kernel.square'})
# Landsat.TOA
# Calibrates Landsat DN to TOA reflectance and brightness temperature for
# Landsat and similar data. For recently-acquired scenes calibration
# coefficients are extracted from the image metadata; for older scenes the
# coefficients are derived from:  Chander, Gyanesh, Brian L. Markham, and
# Dennis L. Helder. "Summary of current radiometric calibration coefficients
# for Landsat MSS, TM, ETM+, and EO-1 ALI sensors." Remote sensing of
# environment 113.5 (2009): 893-903.
#
# Args:
#   input: The Landsat image to process.
signatures.append({'args': [{'description': 'The Landsat image to process.', 'name': 'input', 'type': 'Image'}], 'description': 'Calibrates Landsat DN to TOA reflectance and brightness temperature for Landsat and similar data. For recently-acquired scenes calibration coefficients are extracted from the image metadata; for older scenes the coefficients are derived from:\n Chander, Gyanesh, Brian L. Markham, and Dennis L. Helder. "Summary of current radiometric calibration coefficients for Landsat MSS, TM, ETM+, and EO-1 ALI sensors." Remote sensing of environment 113.5 (2009): 893-903.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Landsat.TOA'})
# Landsat.calibratedRadiance
# Calibrates each band of an image by applying linear transformation with
# slope RADIANCE_MULT_BAND_N and y-intercept RADIANCE_ADD_BAND_N; these
# values are extracted from the image metadata.
#
# Args:
#   image: The input Landsat image.
signatures.append({'args': [{'description': 'The input Landsat image.', 'name': 'image', 'type': 'Image'}], 'description': 'Calibrates each band of an image by applying linear transformation with slope RADIANCE_MULT_BAND_N and y-intercept RADIANCE_ADD_BAND_N; these values are extracted from the image metadata.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Landsat.calibratedRadiance'})
# Landsat.pathRowLimit
# Limits requests to an ImageCollection of Landsat scenes to return a
# controllable number of the best scenes for each request. This is intended
# for use with statistical algorithms like median composites that need a
# certain amount of good data to perform well, but that do not benefit
# substantially from additional data beyond that while becoming needlessly
# expensive.  The default arguments select approximately one year's worth of
# good data.  Note that in rare circumstances, when the tile boundary aligns
# with a Landsat WRS cell bounadry, queries for adjacent tiles may yield
# conflicting results.  This is why it is important that this algorithm only
# be used with statistical methods that can tolerate these inconsistencies.
#
# Args:
#   collection: The Landsat ImageCollection to limit.
#   maxScenesPerPathRow: The max number of scenes to
#       return per path/row.
#   maxScenesTotal: The max number of scenes to return per
#       request total.
signatures.append({'args': [{'description': 'The Landsat ImageCollection to limit.', 'name': 'collection', 'type': 'ImageCollection'}, {'default': 25, 'description': 'The max number of scenes to return per path/row.', 'name': 'maxScenesPerPathRow', 'optional': True, 'type': 'Integer'}, {'default': 100, 'description': 'The max number of scenes to return per request total.', 'name': 'maxScenesTotal', 'optional': True, 'type': 'Integer'}], 'description': "Limits requests to an ImageCollection of Landsat scenes to return a controllable number of the best scenes for each request. This is intended for use with statistical algorithms like median composites that need a certain amount of good data to perform well, but that do not benefit substantially from additional data beyond that while becoming needlessly expensive.  The default arguments select approximately one year's worth of good data.\n\nNote that in rare circumstances, when the tile boundary aligns with a Landsat WRS cell bounadry, queries for adjacent tiles may yield conflicting results.  This is why it is important that this algorithm only be used with statistical methods that can tolerate these inconsistencies.", 'returns': 'ImageCollection', 'type': 'Algorithm', 'hidden': False, 'name': 'Landsat.pathRowLimit'})
# Landsat.simpleCloudScore
# Computes a simple cloud-likelihood score in the range [0,100] using a
# combination of brightness, temperature, and NDSI.  This is not a robust
# cloud detector, and is intended mainly to compare multiple looks at the
# same point for *relative* cloud likelihood.
#
# Args:
#   image: The Landsat TOA image to process.
signatures.append({'args': [{'description': 'The Landsat TOA image to process.', 'name': 'image', 'type': 'Image'}], 'description': 'Computes a simple cloud-likelihood score in the range [0,100] using a combination of brightness, temperature, and NDSI.  This is not a robust cloud detector, and is intended mainly to compare multiple looks at the same point for *relative* cloud likelihood.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Landsat.simpleCloudScore'})
# Landsat.simpleComposite
# Computes a Landsat TOA composite from a collection of raw Landsat scenes.
# It applies standard TOA calibration and then assigns a cloud score to each
# pixel using the SimpleLandsatCloudScore algorithm. It selects the lowest
# possible range of cloud scores at each point and then computes per-band
# percentile values from the accepted pixels.  This algorithm also uses the
# LandsatPathRowLimit algorithm to select only the least-cloudy scenes in
# regions where more than maxDepth input scenes are available.
#
# Args:
#   collection: The raw Landsat ImageCollection to composite.
#   percentile: The percentile value to use when compositing
#       each band.
#   cloudScoreRange: The size of the range of cloud scores
#       to accept per pixel.
#   maxDepth: An approximate limit on the maximum number of
#       scenes used to compute each pixel.
#   asFloat: If true, output bands are in the same units as the
#       Landsat.TOA algorithm; if false, TOA values are converted
#       to uint8 by multiplying by 255 (reflective bands) or
#       subtracting 100 (thermal bands) and rounding to the
#       nearest integer.
signatures.append({'args': [{'description': 'The raw Landsat ImageCollection to composite.', 'name': 'collection', 'type': 'ImageCollection'}, {'default': 50, 'description': 'The percentile value to use when compositing each band.', 'name': 'percentile', 'optional': True, 'type': 'Integer'}, {'default': 10, 'description': 'The size of the range of cloud scores to accept per pixel.', 'name': 'cloudScoreRange', 'optional': True, 'type': 'Integer'}, {'default': 40, 'description': 'An approximate limit on the maximum number of scenes used to compute each pixel.', 'name': 'maxDepth', 'optional': True, 'type': 'Integer'}, {'default': False, 'description': 'If true, output bands are in the same units as the Landsat.TOA algorithm; if false, TOA values are converted to uint8 by multiplying by 255 (reflective bands) or subtracting 100 (thermal bands) and rounding to the nearest integer.', 'name': 'asFloat', 'optional': True, 'type': 'Boolean'}], 'description': 'Computes a Landsat TOA composite from a collection of raw Landsat scenes.  It applies standard TOA calibration and then assigns a cloud score to each pixel using the SimpleLandsatCloudScore algorithm. It selects the lowest possible range of cloud scores at each point and then computes per-band percentile values from the accepted pixels.  This algorithm also uses the LandsatPathRowLimit algorithm to select only the least-cloudy scenes in regions where more than maxDepth input scenes are available.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Landsat.simpleComposite'})
# Landsat.translateMetadata
# Does nothing
#
# Args:
#   input: The asset to wrap.
signatures.append({'args': [{'description': 'The asset to wrap.', 'name': 'input', 'type': 'Image'}], 'description': 'Does nothing', 'returns': 'Image', 'type': 'Algorithm', 'hidden': True, 'name': 'Landsat.translateMetadata'})
# List.add
# Appends the element to the end of list.
#
# Args:
#   list
#   element
signatures.append({'args': [{'name': 'list', 'type': 'List'}, {'name': 'element', 'type': 'Object'}], 'description': 'Appends the element to the end of list.', 'returns': 'List', 'type': 'Algorithm', 'hidden': False, 'name': 'List.add'})
# List.cat
# Concatenates the contents of other onto list.
#
# Args:
#   list
#   other
signatures.append({'args': [{'name': 'list', 'type': 'List'}, {'name': 'other', 'type': 'List'}], 'description': 'Concatenates the contents of other onto list.', 'returns': 'List', 'type': 'Algorithm', 'hidden': False, 'name': 'List.cat'})
# List.contains
# Returns true if list contains element.
#
# Args:
#   list
#   element
signatures.append({'args': [{'name': 'list', 'type': 'List'}, {'name': 'element', 'type': 'Object'}], 'description': 'Returns true if list contains element.', 'returns': 'Boolean', 'type': 'Algorithm', 'hidden': False, 'name': 'List.contains'})
# List.containsAll
# Returns true if list contains all of the elements of other, regardless of
# order.
#
# Args:
#   list
#   other
signatures.append({'args': [{'name': 'list', 'type': 'List'}, {'name': 'other', 'type': 'List'}], 'description': 'Returns true if list contains all of the elements of other, regardless of order.', 'returns': 'Boolean', 'type': 'Algorithm', 'hidden': False, 'name': 'List.containsAll'})
# List.equals
# Returns true if list contains the same elements as other, in the same
# order.
#
# Args:
#   list
#   other
signatures.append({'args': [{'name': 'list', 'type': 'List'}, {'name': 'other', 'type': 'List'}], 'description': 'Returns true if list contains the same elements as other, in the same order.', 'returns': 'Boolean', 'type': 'Algorithm', 'hidden': False, 'name': 'List.equals'})
# List.filter
# Filters a list to only the elements that match the given filter. To filter
# list items that aren't images or features, test a property named'item',
# e.g.: ee.Filter.gt('item', 3)
#
# Args:
#   list
#   filter
signatures.append({'args': [{'name': 'list', 'type': 'List'}, {'name': 'filter', 'type': 'Filter'}], 'description': "Filters a list to only the elements that match the given filter. To filter list items that aren't images or features, test a property named'item', e.g.: ee.Filter.gt('item', 3)", 'returns': 'List', 'type': 'Algorithm', 'hidden': False, 'name': 'List.filter'})
# List.flatten
# Flattens any sublists into a single list.
#
# Args:
#   list
signatures.append({'args': [{'name': 'list', 'type': 'List'}], 'description': 'Flattens any sublists into a single list.', 'returns': 'List', 'type': 'Algorithm', 'hidden': False, 'name': 'List.flatten'})
# List.frequency
# Returns the number of elements in list equal to element.
#
# Args:
#   list
#   element
signatures.append({'args': [{'name': 'list', 'type': 'List'}, {'name': 'element', 'type': 'Object'}], 'description': 'Returns the number of elements in list equal to element.', 'returns': 'Integer', 'type': 'Algorithm', 'hidden': False, 'name': 'List.frequency'})
# List.get
# Returns the element at the specified position in list.  A negative index
# counts backwards from the end of the list.
#
# Args:
#   list
#   index
signatures.append({'args': [{'name': 'list', 'type': 'List'}, {'name': 'index', 'type': 'Integer'}], 'description': 'Returns the element at the specified position in list.  A negative index counts backwards from the end of the list.', 'returns': 'Object', 'type': 'Algorithm', 'hidden': False, 'name': 'List.get'})
# List.indexOf
# Returns the position of the first occurrence of target in list, or -1 if
# list does not contain target.
#
# Args:
#   list
#   element
signatures.append({'args': [{'name': 'list', 'type': 'List'}, {'name': 'element', 'type': 'Object'}], 'description': 'Returns the position of the first occurrence of target in list, or -1 if list does not contain target.', 'returns': 'Integer', 'type': 'Algorithm', 'hidden': False, 'name': 'List.indexOf'})
# List.indexOfSublist
# Returns the starting position of the first occurrence of target within
# list, or -1 if there is no such occurrence.
#
# Args:
#   list
#   target
signatures.append({'args': [{'name': 'list', 'type': 'List'}, {'name': 'target', 'type': 'List'}], 'description': 'Returns the starting position of the first occurrence of target within list, or -1 if there is no such occurrence.', 'returns': 'Integer', 'type': 'Algorithm', 'hidden': False, 'name': 'List.indexOfSublist'})
# List.insert
# Inserts element at the specified position in list. A negative index counts
# backwards from the end of the list.
#
# Args:
#   list
#   index
#   element
signatures.append({'args': [{'name': 'list', 'type': 'List'}, {'name': 'index', 'type': 'Integer'}, {'name': 'element', 'type': 'Object'}], 'description': 'Inserts element at the specified position in list. A negative index counts backwards from the end of the list.', 'returns': 'List', 'type': 'Algorithm', 'hidden': False, 'name': 'List.insert'})
# List.iterate
# Iterate an algorithm over a list.  The algorithm is expected to take two
# objects, the current list item, and the result from the previous iteration
# or the value of first for the first iteration.
#
# Args:
#   list
#   function
#   first
signatures.append({'args': [{'name': 'list', 'type': 'List'}, {'name': 'function', 'type': 'Algorithm'}, {'name': 'first', 'type': 'Object'}], 'description': 'Iterate an algorithm over a list.  The algorithm is expected to take two objects, the current list item, and the result from the previous iteration or the value of first for the first iteration.', 'returns': 'Object', 'type': 'Algorithm', 'hidden': False, 'name': 'List.iterate'})
# List.join
# Returns a string containing the elements of the list joined together with
# the specified separator between elements.
#
# Args:
#   list
#   separator
signatures.append({'args': [{'name': 'list', 'type': 'List'}, {'default': '', 'name': 'separator', 'optional': True, 'type': 'String'}], 'description': 'Returns a string containing the elements of the list joined together with the specified separator between elements.', 'returns': 'String', 'type': 'Algorithm', 'hidden': False, 'name': 'List.join'})
# List.lastIndexOfSubList
# Returns the starting position of the last occurrence of target within list,
# or -1 if there is no such occurrence.
#
# Args:
#   list
#   target
signatures.append({'args': [{'name': 'list', 'type': 'List'}, {'name': 'target', 'type': 'List'}], 'description': 'Returns the starting position of the last occurrence of target within list, or -1 if there is no such occurrence.', 'returns': 'Integer', 'type': 'Algorithm', 'hidden': False, 'name': 'List.lastIndexOfSubList'})
# List.length
# Returns the number of elements in list.
#
# Args:
#   list
signatures.append({'args': [{'name': 'list', 'type': 'List'}], 'description': 'Returns the number of elements in list.', 'returns': 'Integer', 'type': 'Algorithm', 'hidden': False, 'name': 'List.length'})
# List.map
# Map an algorithm over a list.  The algorithm is expected to take an Object
# and return an Object.
#
# Args:
#   list
#   baseAlgorithm
signatures.append({'args': [{'name': 'list', 'type': 'List'}, {'name': 'baseAlgorithm', 'type': 'Algorithm'}], 'description': 'Map an algorithm over a list.  The algorithm is expected to take an Object and return an Object.', 'returns': 'List', 'type': 'Algorithm', 'hidden': False, 'name': 'List.map'})
# List.reduce
# Apply a reducer to a list.  If the reducer takes more than 1 input, then
# each element in the list is assumed to be a list of inputs.  If the reducer
# returns a single output, it is returned directly, otherwise returns a
# dictionary containing the named reducer outputs.
#
# Args:
#   list
#   reducer
signatures.append({'args': [{'name': 'list', 'type': 'List'}, {'name': 'reducer', 'type': 'Reducer'}], 'description': 'Apply a reducer to a list.  If the reducer takes more than 1 input, then each element in the list is assumed to be a list of inputs.  If the reducer returns a single output, it is returned directly, otherwise returns a dictionary containing the named reducer outputs.', 'returns': 'Object', 'type': 'Algorithm', 'hidden': False, 'name': 'List.reduce'})
# List.remove
# Removes the first occurrence of the specified element from list, if it is
# present.
#
# Args:
#   list
#   element
signatures.append({'args': [{'name': 'list', 'type': 'List'}, {'name': 'element', 'type': 'Object'}], 'description': 'Removes the first occurrence of the specified element from list, if it is present.', 'returns': 'List', 'type': 'Algorithm', 'hidden': False, 'name': 'List.remove'})
# List.removeAll
# Removes from list all of the elements that are contained in other list.
#
# Args:
#   list
#   other
signatures.append({'args': [{'name': 'list', 'type': 'List'}, {'name': 'other', 'type': 'List'}], 'description': 'Removes from list all of the elements that are contained in other list.', 'returns': 'List', 'type': 'Algorithm', 'hidden': False, 'name': 'List.removeAll'})
# List.repeat
# Returns a new list containing value repeated count times.
#
# Args:
#   value
#   count
signatures.append({'args': [{'name': 'value', 'type': 'Object'}, {'name': 'count', 'type': 'Integer'}], 'description': 'Returns a new list containing value repeated count times.', 'returns': 'List', 'type': 'Algorithm', 'hidden': False, 'name': 'List.repeat'})
# List.replace
# Replaces the first occurrence of oldVal in list with newVal.
#
# Args:
#   list
#   oldval
#   newval
signatures.append({'args': [{'name': 'list', 'type': 'List'}, {'name': 'oldval', 'type': 'Object'}, {'name': 'newval', 'type': 'Object'}], 'description': 'Replaces the first occurrence of oldVal in list with newVal.', 'returns': 'List', 'type': 'Algorithm', 'hidden': False, 'name': 'List.replace'})
# List.replaceAll
# Replaces all occurrences of oldVal in list with newVal.
#
# Args:
#   list
#   oldval
#   newval
signatures.append({'args': [{'name': 'list', 'type': 'List'}, {'name': 'oldval', 'type': 'Object'}, {'name': 'newval', 'type': 'Object'}], 'description': 'Replaces all occurrences of oldVal in list with newVal.', 'returns': 'List', 'type': 'Algorithm', 'hidden': False, 'name': 'List.replaceAll'})
# List.reverse
# Reverses the order of the elements in list.
#
# Args:
#   list
signatures.append({'args': [{'name': 'list', 'type': 'List'}], 'description': 'Reverses the order of the elements in list.', 'returns': 'List', 'type': 'Algorithm', 'hidden': False, 'name': 'List.reverse'})
# List.rotate
# Rotates the elements of the list by the specified distance.
#
# Args:
#   list
#   distance
signatures.append({'args': [{'name': 'list', 'type': 'List'}, {'name': 'distance', 'type': 'Integer'}], 'description': 'Rotates the elements of the list by the specified distance.', 'returns': 'List', 'type': 'Algorithm', 'hidden': False, 'name': 'List.rotate'})
# List.sequence
# Generate a sequence of numbers from start to end (inclusive) in increments
# of step, or in count equally-spaced increments.  If end is not specified it
# is computed from start + step * count, so at least one of end or count must
# be specified.
#
# Args:
#   start
#   end
#   step
#   count
signatures.append({'args': [{'name': 'start', 'type': 'Number'}, {'default': None, 'name': 'end', 'optional': True, 'type': 'Number'}, {'default': 1.0, 'name': 'step', 'optional': True, 'type': 'Number'}, {'default': None, 'name': 'count', 'optional': True, 'type': 'Integer'}], 'description': 'Generate a sequence of numbers from start to end (inclusive) in increments of step, or in count equally-spaced increments.  If end is not specified it is computed from start + step * count, so at least one of end or count must be specified.', 'returns': 'List', 'type': 'Algorithm', 'hidden': False, 'name': 'List.sequence'})
# List.set
# Replaces the value at the specified position in list with element.  A
# negative index counts backwards from the end of the list.
#
# Args:
#   list
#   index
#   element
signatures.append({'args': [{'name': 'list', 'type': 'List'}, {'name': 'index', 'type': 'Integer'}, {'name': 'element', 'type': 'Object'}], 'description': 'Replaces the value at the specified position in list with element.  A negative index counts backwards from the end of the list.', 'returns': 'List', 'type': 'Algorithm', 'hidden': False, 'name': 'List.set'})
# List.size
# Returns the number of elements in list.
#
# Args:
#   list
signatures.append({'args': [{'name': 'list', 'type': 'List'}], 'description': 'Returns the number of elements in list.', 'returns': 'Integer', 'type': 'Algorithm', 'hidden': False, 'name': 'List.size'})
# List.slice
# Returns a portion of list between the start index, inclusive, and end
# index, exclusive.  Negative values for start or end count backwards from
# the end of the list.  Values greater than the size of the list are legal
# but are truncated to the size of list.
#
# Args:
#   list
#   start
#   end
signatures.append({'args': [{'name': 'list', 'type': 'List'}, {'name': 'start', 'type': 'Integer'}, {'default': None, 'name': 'end', 'optional': True, 'type': 'Integer'}], 'description': 'Returns a portion of list between the start index, inclusive, and end index, exclusive.  Negative values for start or end count backwards from the end of the list.  Values greater than the size of the list are legal but are truncated to the size of list.', 'returns': 'List', 'type': 'Algorithm', 'hidden': False, 'name': 'List.slice'})
# List.sort
# Sorts the list into ascending order.
#
# Args:
#   list
signatures.append({'args': [{'name': 'list', 'type': 'List'}], 'description': 'Sorts the list into ascending order.', 'returns': 'List', 'type': 'Algorithm', 'hidden': False, 'name': 'List.sort'})
# List.splice
# Starting at the start index, removes count elements from list and insert
# the contents of other at that location.  If start is negative, it counts
# backwards from the end of the list.
#
# Args:
#   list
#   start
#   count
#   other
signatures.append({'args': [{'name': 'list', 'type': 'List'}, {'name': 'start', 'type': 'Integer'}, {'name': 'count', 'type': 'Integer'}, {'default': None, 'name': 'other', 'optional': True, 'type': 'List'}], 'description': 'Starting at the start index, removes count elements from list and insert the contents of other at that location.  If start is negative, it counts backwards from the end of the list.', 'returns': 'List', 'type': 'Algorithm', 'hidden': False, 'name': 'List.splice'})
# List.swap
# Swaps the elements at the specified positions.  A negative position counts
# backwards from the end of the list.
#
# Args:
#   list
#   pos1
#   pos2
signatures.append({'args': [{'name': 'list', 'type': 'List'}, {'name': 'pos1', 'type': 'Integer'}, {'name': 'pos2', 'type': 'Integer'}], 'description': 'Swaps the elements at the specified positions.  A negative position counts backwards from the end of the list.', 'returns': 'List', 'type': 'Algorithm', 'hidden': False, 'name': 'List.swap'})
# List.zip
# Pairs the elements of two lists to create a list of two-element lists.
# When the input lists are of different sizes, the final list has the same
# size as the shortest one.
#
# Args:
#   list
#   other
signatures.append({'args': [{'name': 'list', 'type': 'List'}, {'name': 'other', 'type': 'List'}], 'description': 'Pairs the elements of two lists to create a list of two-element lists.  When the input lists are of different sizes, the final list has the same size as the shortest one.', 'returns': 'List', 'type': 'Algorithm', 'hidden': False, 'name': 'List.zip'})
# Number.abs
# Computes the absolute value of the input.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Computes the absolute value of the input.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.abs'})
# Number.acos
# Computes the arc cosine in radians of the input.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Computes the arc cosine in radians of the input.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.acos'})
# Number.add
# Adds the first value to the second.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Number'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Number'}], 'description': 'Adds the first value to the second.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.add'})
# Number.and
# Returns 1 iff both values are non-zero.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Number'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Number'}], 'description': 'Returns 1 iff both values are non-zero.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.and'})
# Number.asin
# Computes the arc sine in radians of the input.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Computes the arc sine in radians of the input.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.asin'})
# Number.atan
# Computes the arc tangent in radians of the input.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Computes the arc tangent in radians of the input.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.atan'})
# Number.atan2
# Calculates the angle formed by the 2D vector [x, y].
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Number'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Number'}], 'description': 'Calculates the angle formed by the 2D vector [x, y].', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.atan2'})
# Number.bitCount
# Calculates the number of one-bits in the 64-bit two's complement binary
# representation of the input.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': "Calculates the number of one-bits in the 64-bit two's complement binary representation of the input.", 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.bitCount'})
# Number.bitwiseAnd
# Calculates the bitwise AND of the input values.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Number'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Number'}], 'description': 'Calculates the bitwise AND of the input values.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.bitwiseAnd'})
# Number.bitwiseNot
# Calculates the bitwise NOT of the input, in the smallest signed integer
# type that can hold the input.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Calculates the bitwise NOT of the input, in the smallest signed integer type that can hold the input.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.bitwiseNot'})
# Number.bitwiseOr
# Calculates the bitwise OR of the input values.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Number'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Number'}], 'description': 'Calculates the bitwise OR of the input values.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.bitwiseOr'})
# Number.bitwiseXor
# Calculates the bitwise XOR of the input values.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Number'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Number'}], 'description': 'Calculates the bitwise XOR of the input values.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.bitwiseXor'})
# Number.bitwise_and
# Calculates the bitwise AND of the input values.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Number'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Number'}], 'description': 'Calculates the bitwise AND of the input values.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.bitwise_and'})
# Number.bitwise_not
# Calculates the bitwise NOT of the input, in the smallest signed integer
# type that can hold the input.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Calculates the bitwise NOT of the input, in the smallest signed integer type that can hold the input.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.bitwise_not'})
# Number.bitwise_or
# Calculates the bitwise OR of the input values.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Number'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Number'}], 'description': 'Calculates the bitwise OR of the input values.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.bitwise_or'})
# Number.bitwise_xor
# Calculates the bitwise XOR of the input values.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Number'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Number'}], 'description': 'Calculates the bitwise XOR of the input values.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.bitwise_xor'})
# Number.byte
# Casts the input value to an unsigned 8-bit integer.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Casts the input value to an unsigned 8-bit integer.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.byte'})
# Number.cbrt
# Computes the cubic root of the input.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Computes the cubic root of the input.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.cbrt'})
# Number.ceil
# Computes the smallest integer greater than or equal to the input.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Computes the smallest integer greater than or equal to the input.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.ceil'})
# Number.cos
# Computes the cosine of the input in radians.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Computes the cosine of the input in radians.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.cos'})
# Number.cosh
# Computes the hyperbolic cosine of the input.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Computes the hyperbolic cosine of the input.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.cosh'})
# Number.digamma
# Computes the digamma function of the input.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Computes the digamma function of the input.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.digamma'})
# Number.divide
# Divides the first value by the second, returning 0 for division by 0.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Number'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Number'}], 'description': 'Divides the first value by the second, returning 0 for division by 0.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.divide'})
# Number.double
# Casts the input value to a 64-bit float.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Casts the input value to a 64-bit float.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.double'})
# Number.eq
# Returns 1 iff the first value is equal to the second.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Number'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Number'}], 'description': 'Returns 1 iff the first value is equal to the second.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.eq'})
# Number.erf
# Computes the error function of the input.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Computes the error function of the input.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.erf'})
# Number.erfInv
# Computes the inverse error function of the input.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Computes the inverse error function of the input.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.erfInv'})
# Number.erfc
# Computes the complementary error function of the input.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Computes the complementary error function of the input.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.erfc'})
# Number.erfcInv
# Computes the inverse complementary error function of the input.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Computes the inverse complementary error function of the input.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.erfcInv'})
# Number.exp
# Computes the Euler's number e raised to the power of the input.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': "Computes the Euler's number e raised to the power of the input.", 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.exp'})
# Number.first
# Selects the value of the first value.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Number'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Number'}], 'description': 'Selects the value of the first value.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.first'})
# Number.firstNonZero
# Selects the first value if it is non-zero, and the second value otherwise.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Number'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Number'}], 'description': 'Selects the first value if it is non-zero, and the second value otherwise.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.firstNonZero'})
# Number.first_nonzero
# Selects the first value if it is non-zero, and the second value otherwise.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Number'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Number'}], 'description': 'Selects the first value if it is non-zero, and the second value otherwise.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.first_nonzero'})
# Number.float
# Casts the input value to a 32-bit float.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Casts the input value to a 32-bit float.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.float'})
# Number.floor
# Computes the largest integer less than or equal to the input.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Computes the largest integer less than or equal to the input.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.floor'})
# Number.format
# Convert a number to a string using printf-style formatting.
#
# Args:
#   number: The number to convert to a string.
#   pattern: A printf-style format string. For example, '%.2f'
#       produces numbers formatted like '3.14', and '%05d'
#       produces numbers formatted like '00042'. The format string
#       must satisfy the following criteria: 1. Zero or more
#       prefix characters. 2. Exactly one '%'. 3. Zero or more
#       modifier characters in the set [#-+ 0,(.\d]. 4. Exactly
#       one conversion character in the set [sdoxXeEfgGaA]. 5.
#       Zero or more suffix characters.   For more about format
#       strings, see https://docs.oracle.com/javase/7/docs/api/jav
#       a/util/Formatter.html
signatures.append({'args': [{'description': 'The number to convert to a string.', 'name': 'number', 'type': 'Number'}, {'default': '%s', 'description': "A printf-style format string. For example, '%.2f' produces numbers formatted like '3.14', and '%05d' produces numbers formatted like '00042'. The format string must satisfy the following criteria:\n1. Zero or more prefix characters.\n2. Exactly one '%'.\n3. Zero or more modifier characters in the set [#-+ 0,(.\\d].\n4. Exactly one conversion character in the set [sdoxXeEfgGaA].\n5. Zero or more suffix characters.\n \nFor more about format strings, see https://docs.oracle.com/javase/7/docs/api/java/util/Formatter.html", 'name': 'pattern', 'optional': True, 'type': 'String'}], 'description': 'Convert a number to a string using printf-style formatting.', 'returns': 'String', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.format'})
# Number.gamma
# Computes the gamma function of the input.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Computes the gamma function of the input.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.gamma'})
# Number.gammainc
# Calculates the regularized lower incomplete Gamma function (&gamma;(x,a).
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Number'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Number'}], 'description': 'Calculates the regularized lower incomplete Gamma function (&gamma;(x,a).', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.gammainc'})
# Number.gt
# Returns 1 iff the first value is greater than the second.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Number'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Number'}], 'description': 'Returns 1 iff the first value is greater than the second.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.gt'})
# Number.gte
# Returns 1 iff the first value is greater than or equal to the second.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Number'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Number'}], 'description': 'Returns 1 iff the first value is greater than or equal to the second.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.gte'})
# Number.hypot
# Calculates the magnitude of the 2D vector [x, y].
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Number'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Number'}], 'description': 'Calculates the magnitude of the 2D vector [x, y].', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.hypot'})
# Number.int
# Casts the input value to a signed 32-bit integer.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Casts the input value to a signed 32-bit integer.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.int'})
# Number.int16
# Casts the input value to a signed 16-bit integer.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Casts the input value to a signed 16-bit integer.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.int16'})
# Number.int32
# Casts the input value to a signed 32-bit integer.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Casts the input value to a signed 32-bit integer.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.int32'})
# Number.int64
# Casts the input value to a signed 64-bit integer.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Casts the input value to a signed 64-bit integer.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.int64'})
# Number.int8
# Casts the input value to a signed 8-bit integer.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Casts the input value to a signed 8-bit integer.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.int8'})
# Number.lanczos
# Computes the Lanczos approximation of the input.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Computes the Lanczos approximation of the input.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.lanczos'})
# Number.leftShift
# Calculates the left shift of v1 by v2 bits.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Number'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Number'}], 'description': 'Calculates the left shift of v1 by v2 bits.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.leftShift'})
# Number.left_shift
# Calculates the left shift of v1 by v2 bits.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Number'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Number'}], 'description': 'Calculates the left shift of v1 by v2 bits.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.left_shift'})
# Number.log
# Computes the natural logarithm of the input.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Computes the natural logarithm of the input.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.log'})
# Number.log10
# Computes the base-10 logarithm of the input.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Computes the base-10 logarithm of the input.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.log10'})
# Number.long
# Casts the input value to a signed 64-bit integer.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Casts the input value to a signed 64-bit integer.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.long'})
# Number.lt
# Returns 1 iff the first value is less than the second.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Number'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Number'}], 'description': 'Returns 1 iff the first value is less than the second.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.lt'})
# Number.lte
# Returns 1 iff the first value is less than or equal to the second.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Number'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Number'}], 'description': 'Returns 1 iff the first value is less than or equal to the second.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.lte'})
# Number.max
# Selects the maximum of the first and second values.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Number'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Number'}], 'description': 'Selects the maximum of the first and second values.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.max'})
# Number.min
# Selects the minimum of the first and second values.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Number'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Number'}], 'description': 'Selects the minimum of the first and second values.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.min'})
# Number.mod
# Calculates the remainder of the first value divided by the second.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Number'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Number'}], 'description': 'Calculates the remainder of the first value divided by the second.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.mod'})
# Number.multiply
# Multiplies the first value by the second.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Number'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Number'}], 'description': 'Multiplies the first value by the second.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.multiply'})
# Number.neq
# Returns 1 iff the first value is not equal to the second.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Number'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Number'}], 'description': 'Returns 1 iff the first value is not equal to the second.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.neq'})
# Number.not
# Returns 0 if the input is non-zero, and 1 otherwise.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Returns 0 if the input is non-zero, and 1 otherwise.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.not'})
# Number.or
# Returns 1 iff either input value is non-zero.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Number'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Number'}], 'description': 'Returns 1 iff either input value is non-zero.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.or'})
# Number.parse
# Convert a string to a number.
#
# Args:
#   input: The string to convert to a number.
#   radix: An integer representing the base number system from which
#       to convert. If input is not an integer, radix must equal 10
#       or not be specified.
signatures.append({'args': [{'description': 'The string to convert to a number.', 'name': 'input', 'type': 'String'}, {'default': 10, 'description': 'An integer representing the base number system from which to convert. If input is not an integer, radix must equal 10 or not be specified.', 'name': 'radix', 'optional': True, 'type': 'Integer'}], 'description': 'Convert a string to a number.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.parse'})
# Number.pow
# Raises the first value to the power of the second.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Number'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Number'}], 'description': 'Raises the first value to the power of the second.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.pow'})
# Number.rightShift
# Calculates the signed right shift of v1 by v2 bits.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Number'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Number'}], 'description': 'Calculates the signed right shift of v1 by v2 bits.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.rightShift'})
# Number.right_shift
# Calculates the signed right shift of v1 by v2 bits.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Number'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Number'}], 'description': 'Calculates the signed right shift of v1 by v2 bits.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.right_shift'})
# Number.round
# Computes the integer nearest to the input.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Computes the integer nearest to the input.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.round'})
# Number.short
# Casts the input value to a signed 16-bit integer.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Casts the input value to a signed 16-bit integer.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.short'})
# Number.sin
# Computes the sine of the input in radians.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Computes the sine of the input in radians.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.sin'})
# Number.sinh
# Computes the hyperbolic sine of the input.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Computes the hyperbolic sine of the input.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.sinh'})
# Number.sqrt
# Computes the square root of the input.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Computes the square root of the input.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.sqrt'})
# Number.subtract
# Subtracts the second value from the first.
#
# Args:
#   left: The left-hand value.
#   right: The right-hand value.
signatures.append({'args': [{'description': 'The left-hand value.', 'name': 'left', 'type': 'Number'}, {'description': 'The right-hand value.', 'name': 'right', 'type': 'Number'}], 'description': 'Subtracts the second value from the first.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.subtract'})
# Number.tan
# Computes the tangent of the input in radians.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Computes the tangent of the input in radians.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.tan'})
# Number.tanh
# Computes the hyperbolic tangent of the input.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Computes the hyperbolic tangent of the input.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.tanh'})
# Number.toByte
# Casts the input value to an unsigned 8-bit integer.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Casts the input value to an unsigned 8-bit integer.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.toByte'})
# Number.toDouble
# Casts the input value to a 64-bit float.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Casts the input value to a 64-bit float.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.toDouble'})
# Number.toFloat
# Casts the input value to a 32-bit float.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Casts the input value to a 32-bit float.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.toFloat'})
# Number.toInt
# Casts the input value to a signed 32-bit integer.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Casts the input value to a signed 32-bit integer.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.toInt'})
# Number.toInt16
# Casts the input value to a signed 16-bit integer.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Casts the input value to a signed 16-bit integer.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.toInt16'})
# Number.toInt32
# Casts the input value to a signed 32-bit integer.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Casts the input value to a signed 32-bit integer.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.toInt32'})
# Number.toInt64
# Casts the input value to a signed 64-bit integer.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Casts the input value to a signed 64-bit integer.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.toInt64'})
# Number.toInt8
# Casts the input value to a signed 8-bit integer.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Casts the input value to a signed 8-bit integer.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.toInt8'})
# Number.toLong
# Casts the input value to a signed 64-bit integer.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Casts the input value to a signed 64-bit integer.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.toLong'})
# Number.toShort
# Casts the input value to a signed 16-bit integer.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Casts the input value to a signed 16-bit integer.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.toShort'})
# Number.toUint16
# Casts the input value to an unsigned 16-bit integer.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Casts the input value to an unsigned 16-bit integer.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.toUint16'})
# Number.toUint32
# Casts the input value to an unsigned 32-bit integer.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Casts the input value to an unsigned 32-bit integer.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.toUint32'})
# Number.toUint8
# Casts the input value to an unsigned 8-bit integer.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Casts the input value to an unsigned 8-bit integer.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.toUint8'})
# Number.trigamma
# Computes the trigamma function of the input.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Computes the trigamma function of the input.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.trigamma'})
# Number.uint16
# Casts the input value to an unsigned 16-bit integer.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Casts the input value to an unsigned 16-bit integer.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.uint16'})
# Number.uint32
# Casts the input value to an unsigned 32-bit integer.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Casts the input value to an unsigned 32-bit integer.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.uint32'})
# Number.uint8
# Casts the input value to an unsigned 8-bit integer.
#
# Args:
#   input: The input value.
signatures.append({'args': [{'description': 'The input value.', 'name': 'input', 'type': 'Number'}], 'description': 'Casts the input value to an unsigned 8-bit integer.', 'returns': 'Number', 'type': 'Algorithm', 'hidden': False, 'name': 'Number.uint8'})
# PixelType
# Returns a PixelType of the given precision with the given limits per
# element, and an optional dimensionality.
#
# Args:
#   precision: The pixel precision, one of 'int', 'float', or
#       'double'.
#   minValue: The minimum value of pixels of this type. If
#       precision is 'float' or 'double', this can be null,
#       signifying negative infinity.
#   maxValue: The maximum value of pixels of this type. If
#       precision is 'float' or 'double', this can be null,
#       signifying positive infinity.
#   dimensions: The number of dimensions in which pixels of
#       this type can vary; 0 is a scalar, 1 is a vector, 2 is
#       a matrix, etc.
signatures.append({'args': [{'description': "The pixel precision, one of 'int', 'float', or 'double'.", 'name': 'precision', 'type': 'Object'}, {'default': None, 'description': "The minimum value of pixels of this type. If precision is 'float' or 'double', this can be null, signifying negative infinity.", 'name': 'minValue', 'optional': True, 'type': 'Number'}, {'default': None, 'description': "The maximum value of pixels of this type. If precision is 'float' or 'double', this can be null, signifying positive infinity.", 'name': 'maxValue', 'optional': True, 'type': 'Number'}, {'default': 0, 'description': 'The number of dimensions in which pixels of this type can vary; 0 is a scalar, 1 is a vector, 2 is a matrix, etc.', 'name': 'dimensions', 'optional': True, 'type': 'Integer'}], 'description': 'Returns a PixelType of the given precision with the given limits per element, and an optional dimensionality.', 'returns': 'PixelType', 'type': 'Algorithm', 'hidden': False, 'name': 'PixelType'})
# PixelType.double
# Returns the 64-bit floating point pixel type.
signatures.append({'args': [], 'description': 'Returns the 64-bit floating point pixel type.', 'returns': 'PixelType', 'type': 'Algorithm', 'hidden': False, 'name': 'PixelType.double'})
# PixelType.float
# Returns the 32-bit floating point pixel type.
signatures.append({'args': [], 'description': 'Returns the 32-bit floating point pixel type.', 'returns': 'PixelType', 'type': 'Algorithm', 'hidden': False, 'name': 'PixelType.float'})
# PixelType.int16
# Returns the 16-bit signed integer pixel type.
signatures.append({'args': [], 'description': 'Returns the 16-bit signed integer pixel type.', 'returns': 'PixelType', 'type': 'Algorithm', 'hidden': False, 'name': 'PixelType.int16'})
# PixelType.int32
# Returns the 32-bit signed integer pixel type.
signatures.append({'args': [], 'description': 'Returns the 32-bit signed integer pixel type.', 'returns': 'PixelType', 'type': 'Algorithm', 'hidden': False, 'name': 'PixelType.int32'})
# PixelType.int64
# Returns the 64-bit signed integer pixel type.
signatures.append({'args': [], 'description': 'Returns the 64-bit signed integer pixel type.', 'returns': 'PixelType', 'type': 'Algorithm', 'hidden': False, 'name': 'PixelType.int64'})
# PixelType.int8
# Returns the 8-bit signed integer pixel type.
signatures.append({'args': [], 'description': 'Returns the 8-bit signed integer pixel type.', 'returns': 'PixelType', 'type': 'Algorithm', 'hidden': False, 'name': 'PixelType.int8'})
# PixelType.uint16
# Returns the 16-bit unsigned integer pixel type.
signatures.append({'args': [], 'description': 'Returns the 16-bit unsigned integer pixel type.', 'returns': 'PixelType', 'type': 'Algorithm', 'hidden': False, 'name': 'PixelType.uint16'})
# PixelType.uint32
# Returns the 32-bit unsigned integer pixel type.
signatures.append({'args': [], 'description': 'Returns the 32-bit unsigned integer pixel type.', 'returns': 'PixelType', 'type': 'Algorithm', 'hidden': False, 'name': 'PixelType.uint32'})
# PixelType.uint8
# Returns the 8-bit unsigned integer pixel type.
signatures.append({'args': [], 'description': 'Returns the 8-bit unsigned integer pixel type.', 'returns': 'PixelType', 'type': 'Algorithm', 'hidden': False, 'name': 'PixelType.uint8'})
# PointMatcher.PointMatcherContainer
# INTERNAL
#
# Args:
#   templateImage: The image containing the point to align.
#   searchImage
#   x
#   y
#   proj
#   maxOffset
#   templateBandNames
#   searchBandNames
#   windowSize
#   expectedXOffset
#   expectedYOffset
#   maxResults
#   maxMaskedFrac
signatures.append({'args': [{'description': 'The image containing the point to align.', 'name': 'templateImage', 'type': 'Image'}, {'name': 'searchImage', 'type': 'Image'}, {'name': 'x', 'type': 'Integer'}, {'name': 'y', 'type': 'Integer'}, {'name': 'proj', 'type': 'Projection'}, {'name': 'maxOffset', 'type': 'Integer'}, {'default': None, 'name': 'templateBandNames', 'optional': True, 'type': 'List'}, {'default': None, 'name': 'searchBandNames', 'optional': True, 'type': 'List'}, {'default': 15, 'name': 'windowSize', 'optional': True, 'type': 'Integer'}, {'default': 0, 'name': 'expectedXOffset', 'optional': True, 'type': 'Integer'}, {'default': 0, 'name': 'expectedYOffset', 'optional': True, 'type': 'Integer'}, {'default': 1, 'name': 'maxResults', 'optional': True, 'type': 'Integer'}, {'default': 0.0, 'name': 'maxMaskedFrac', 'optional': True, 'type': 'Float'}], 'description': 'INTERNAL', 'returns': 'Image', 'type': 'Algorithm', 'hidden': True, 'name': 'PointMatcher.PointMatcherContainer'})
# Profile.getProfiles
# Retrieve computation profile data given profile IDs.
#
# Args:
#   ids: One or more profile IDs returned by previous computations.
#   format: Format to return data in, either 'text' or 'json'.
signatures.append({'args': [{'description': 'One or more profile IDs returned by previous computations.', 'name': 'ids', 'type': 'List'}, {'default': 'text', 'description': "Format to return data in, either 'text' or 'json'.", 'name': 'format', 'optional': True, 'type': 'String'}], 'description': 'Retrieve computation profile data given profile IDs.', 'returns': 'Object', 'type': 'Algorithm', 'hidden': True, 'name': 'Profile.getProfiles'})
# Proj
# Returns a Projection with the given base coordinate system and the given
# transform between projected coordinates and the base. If no transform is
# specified, the identity transform is assumed.
#
# Args:
#   crs: The base coordinate reference system of this Projection,
#       given as a well-known authority code (e.g. 'EPSG:4326') or a
#       WKT string.
#   transform: The transform between projected coordinates and
#       the base coordinate system, specified as a 2x3 affine
#       transform matrix in row-major order: [xScale, xShearing,
#       xTranslation, yShearing, yScale, yTranslation]. May not
#       specify both this and 'transformWkt'.
#   transformWkt: The transform between projected coordinates
#       and the base coordinate system, specified as a WKT
#       string. May not specify both this and 'transform'.
signatures.append({'args': [{'description': "The base coordinate reference system of this Projection, given as a well-known authority code (e.g. 'EPSG:4326') or a WKT string.", 'name': 'crs', 'type': 'Object'}, {'default': None, 'description': "The transform between projected coordinates and the base coordinate system, specified as a 2x3 affine transform matrix in row-major order: [xScale, xShearing, xTranslation, yShearing, yScale, yTranslation]. May not specify both this and 'transformWkt'.", 'name': 'transform', 'optional': True, 'type': 'List'}, {'default': None, 'description': "The transform between projected coordinates and the base coordinate system, specified as a WKT string. May not specify both this and 'transform'.", 'name': 'transformWkt', 'optional': True, 'type': 'String'}], 'description': 'Returns a Projection with the given base coordinate system and the given transform between projected coordinates and the base. If no transform is specified, the identity transform is assumed.', 'returns': 'Projection', 'type': 'Algorithm', 'hidden': False, 'deprecated': 'Use Projection().', 'name': 'Proj'})
# Projection
# Returns a Projection with the given base coordinate system and the given
# transform between projected coordinates and the base. If no transform is
# specified, the identity transform is assumed.
#
# Args:
#   crs: The base coordinate reference system of this Projection,
#       given as a well-known authority code (e.g. 'EPSG:4326') or a
#       WKT string.
#   transform: The transform between projected coordinates and
#       the base coordinate system, specified as a 2x3 affine
#       transform matrix in row-major order: [xScale, xShearing,
#       xTranslation, yShearing, yScale, yTranslation]. May not
#       specify both this and 'transformWkt'.
#   transformWkt: The transform between projected coordinates
#       and the base coordinate system, specified as a WKT
#       string. May not specify both this and 'transform'.
signatures.append({'args': [{'description': "The base coordinate reference system of this Projection, given as a well-known authority code (e.g. 'EPSG:4326') or a WKT string.", 'name': 'crs', 'type': 'Object'}, {'default': None, 'description': "The transform between projected coordinates and the base coordinate system, specified as a 2x3 affine transform matrix in row-major order: [xScale, xShearing, xTranslation, yShearing, yScale, yTranslation]. May not specify both this and 'transformWkt'.", 'name': 'transform', 'optional': True, 'type': 'List'}, {'default': None, 'description': "The transform between projected coordinates and the base coordinate system, specified as a WKT string. May not specify both this and 'transform'.", 'name': 'transformWkt', 'optional': True, 'type': 'String'}], 'description': 'Returns a Projection with the given base coordinate system and the given transform between projected coordinates and the base. If no transform is specified, the identity transform is assumed.', 'returns': 'Projection', 'type': 'Algorithm', 'hidden': False, 'name': 'Projection'})
# Projection.atScale
# Returns the projection scaled such that its units have the given scale in
# linear meters, as measured at the point of true scale.
#
# Args:
#   projection
#   meters
signatures.append({'args': [{'name': 'projection', 'type': 'Projection'}, {'name': 'meters', 'type': 'Float'}], 'description': 'Returns the projection scaled such that its units have the given scale in linear meters, as measured at the point of true scale.', 'returns': 'Projection', 'type': 'Algorithm', 'hidden': False, 'name': 'Projection.atScale'})
# Projection.crs
# Returns the authority code (e.g. 'EPSG:4326') for the base coordinate
# system of this projection, or null if the base coordinate system is not
# found in any available database.
#
# Args:
#   projection
signatures.append({'args': [{'name': 'projection', 'type': 'Projection'}], 'description': "Returns the authority code (e.g. 'EPSG:4326') for the base coordinate system of this projection, or null if the base coordinate system is not found in any available database.", 'returns': 'String', 'type': 'Algorithm', 'hidden': False, 'name': 'Projection.crs'})
# Projection.nominalScale
# Returns the linear scale in meters of the units of this projection, as
# measured at the point of true scale.
#
# Args:
#   proj
signatures.append({'args': [{'name': 'proj', 'type': 'Projection'}], 'description': 'Returns the linear scale in meters of the units of this projection, as measured at the point of true scale.', 'returns': 'Float', 'type': 'Algorithm', 'hidden': False, 'name': 'Projection.nominalScale'})
# Projection.scale
# Returns the projection scaled by the given amount in each axis.
#
# Args:
#   projection
#   x
#   y
signatures.append({'args': [{'name': 'projection', 'type': 'Projection'}, {'name': 'x', 'type': 'Float'}, {'name': 'y', 'type': 'Float'}], 'description': 'Returns the projection scaled by the given amount in each axis.', 'returns': 'Projection', 'type': 'Algorithm', 'hidden': False, 'name': 'Projection.scale'})
# Projection.transform
# Returns a WKT representation of the transform of this Projection. This is
# the transform that converts from projected coordinates to the base
# coordinate system.
#
# Args:
#   projection
signatures.append({'args': [{'name': 'projection', 'type': 'Projection'}], 'description': 'Returns a WKT representation of the transform of this Projection. This is the transform that converts from projected coordinates to the base coordinate system.', 'returns': 'String', 'type': 'Algorithm', 'hidden': False, 'name': 'Projection.transform'})
# Projection.translate
# Returns the projection translated by the given amount in each axis.
#
# Args:
#   projection
#   x
#   y
signatures.append({'args': [{'name': 'projection', 'type': 'Projection'}, {'name': 'x', 'type': 'Float'}, {'name': 'y', 'type': 'Float'}], 'description': 'Returns the projection translated by the given amount in each axis.', 'returns': 'Projection', 'type': 'Algorithm', 'hidden': False, 'name': 'Projection.translate'})
# Projection.wkt
# Returns a WKT representation of the base coordinate system of this
# Projection.
#
# Args:
#   projection
signatures.append({'args': [{'name': 'projection', 'type': 'Projection'}], 'description': 'Returns a WKT representation of the base coordinate system of this Projection.', 'returns': 'String', 'type': 'Algorithm', 'hidden': False, 'name': 'Projection.wkt'})
# ProjectionTransform
# Transforms the geometry of a feature to a specific projection.
#
# Args:
#   feature: The feature the geometry of which is being converted.
#   proj: The target projection. Defaults to WGS84. If this has a
#       geographic CRS, the edges of the geometry will be interpreted
#       as geodesics. Otherwise they will be interpreted as straight
#       lines in the projection.
#   maxError: The maximum projection error.
signatures.append({'args': [{'description': 'The feature the geometry of which is being converted.', 'name': 'feature', 'type': 'Element'}, {'default': {'crs': 'EPSG:4326', 'transform': [1.0, 0.0, 0.0, 0.0, 1.0, 0.0], 'type': 'Projection'}, 'description': 'The target projection. Defaults to WGS84. If this has a geographic CRS, the edges of the geometry will be interpreted as geodesics. Otherwise they will be interpreted as straight lines in the projection.', 'name': 'proj', 'optional': True, 'type': 'Projection'}, {'default': None, 'description': 'The maximum projection error.', 'name': 'maxError', 'optional': True, 'type': 'ErrorMargin'}], 'description': 'Transforms the geometry of a feature to a specific projection.', 'returns': 'Feature', 'type': 'Algorithm', 'hidden': False, 'name': 'ProjectionTransform'})
# ReduceRegion.AggregationContainer
# INTERNAL
#
# Args:
#   image
#   proj
#   geom
#   reducer
#   tileScale
signatures.append({'args': [{'name': 'image', 'type': 'Image'}, {'name': 'proj', 'type': 'Projection'}, {'name': 'geom', 'type': 'Geometry'}, {'name': 'reducer', 'type': 'Reducer'}, {'name': 'tileScale', 'type': 'Float'}], 'description': 'INTERNAL', 'returns': 'Image', 'type': 'Algorithm', 'hidden': True, 'name': 'ReduceRegion.AggregationContainer'})
# ReduceRegions.AggregationContainer
# INTERNAL
#
# Args:
#   enumerator
signatures.append({'args': [{'name': 'enumerator', 'type': 'Object'}], 'description': 'INTERNAL', 'returns': 'Image', 'type': 'Algorithm', 'hidden': True, 'name': 'ReduceRegions.AggregationContainer'})
# ReduceRegions.ReduceRegionsEnumerator
# Creates a Object.
#
# Args:
#   image
#   collection
#   reducer
#   proj
#   tileScale
signatures.append({'args': [{'name': 'image', 'type': 'Image'}, {'name': 'collection', 'type': 'FeatureCollection'}, {'name': 'reducer', 'type': 'Reducer'}, {'name': 'proj', 'type': 'Projection'}, {'name': 'tileScale', 'type': 'Float'}], 'description': 'Creates a Object.', 'returns': 'Object', 'type': 'Algorithm', 'hidden': True, 'name': 'ReduceRegions.ReduceRegionsEnumerator'})
# ReduceToVectors.AggregationContainer
# INTERNAL
#
# Args:
#   enumerator
#   filter
signatures.append({'args': [{'name': 'enumerator', 'type': 'Object'}, {'default': None, 'name': 'filter', 'optional': True, 'type': 'Filter'}], 'description': 'INTERNAL', 'returns': 'Image', 'type': 'Algorithm', 'hidden': True, 'name': 'ReduceToVectors.AggregationContainer'})
# ReduceToVectors.ReduceSegmentsEnumerator
# Creates a Object.
#
# Args:
#   image
#   proj
#   geom
#   reducer
#   geometryType
#   eightConnected
#   labelProperty
#   tileScale
#   geometryInNativeProjection
#   streaming
signatures.append({'args': [{'name': 'image', 'type': 'Image'}, {'name': 'proj', 'type': 'Projection'}, {'name': 'geom', 'type': 'Geometry'}, {'name': 'reducer', 'type': 'Reducer'}, {'name': 'geometryType', 'type': 'String'}, {'name': 'eightConnected', 'type': 'Boolean'}, {'name': 'labelProperty', 'type': 'String'}, {'name': 'tileScale', 'type': 'Float'}, {'name': 'geometryInNativeProjection', 'type': 'Boolean'}, {'name': 'streaming', 'type': 'Boolean'}], 'description': 'Creates a Object.', 'returns': 'Object', 'type': 'Algorithm', 'hidden': True, 'name': 'ReduceToVectors.ReduceSegmentsEnumerator'})
# Reducer.allNonZero
# Returns a Reducer that returns 1 if all of its inputs are non-zero, 0
# otherwise.
signatures.append({'args': [], 'description': 'Returns a Reducer that returns 1 if all of its inputs are non-zero, 0 otherwise.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.allNonZero'})
# Reducer.and
# Returns a Reducer that returns 1 if all of its inputs are non-zero, 0
# otherwise.
signatures.append({'args': [], 'description': 'Returns a Reducer that returns 1 if all of its inputs are non-zero, 0 otherwise.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'deprecated': 'Use Reducer.allNonZero().', 'name': 'Reducer.and'})
# Reducer.anyNonZero
# Returns a Reducer that returns 1 if any of its inputs are non-zero, 0
# otherwise.
signatures.append({'args': [], 'description': 'Returns a Reducer that returns 1 if any of its inputs are non-zero, 0 otherwise.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.anyNonZero'})
# Reducer.autoHistogram
# Create a reducer that will compute a histogram of the inputs.  The output
# is a Nx2 array of the lower bucket bounds and the counts of each bucket,
# and is suitable for use per-pixel.
#
# Args:
#   maxBuckets: The maximum number of buckets to use when
#       building a histogram; will be rounded up to a power of
#       2.
#   minBucketWidth: The minimum histogram bucket width, or
#       null to allow any power of 2.
#   maxRaw: The number of values to accumulate before building the
#       initial histogram.
signatures.append({'args': [{'default': None, 'description': 'The maximum number of buckets to use when building a histogram; will be rounded up to a power of 2.', 'name': 'maxBuckets', 'optional': True, 'type': 'Integer'}, {'default': None, 'description': 'The minimum histogram bucket width, or null to allow any power of 2.', 'name': 'minBucketWidth', 'optional': True, 'type': 'Float'}, {'default': None, 'description': 'The number of values to accumulate before building the initial histogram.', 'name': 'maxRaw', 'optional': True, 'type': 'Integer'}], 'description': 'Create a reducer that will compute a histogram of the inputs.  The output is a Nx2 array of the lower bucket bounds and the counts of each bucket, and is suitable for use per-pixel.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.autoHistogram'})
# Reducer.bitwiseAnd
# Returns a Reducer that computes the bitwise-and summation of its inputs.
signatures.append({'args': [], 'description': 'Returns a Reducer that computes the bitwise-and summation of its inputs.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.bitwiseAnd'})
# Reducer.bitwiseOr
# Returns a Reducer that computes the bitwise-or summation of its inputs.
signatures.append({'args': [], 'description': 'Returns a Reducer that computes the bitwise-or summation of its inputs.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.bitwiseOr'})
# Reducer.centeredCovariance
# Creates a reducer that reduces some number of 1-D arrays of the same length
# N to a covariance matrix of shape NxN.  WARNING: this reducer requires that
# the data has been mean centered.
signatures.append({'args': [], 'description': 'Creates a reducer that reduces some number of 1-D arrays of the same length N to a covariance matrix of shape NxN.  WARNING: this reducer requires that the data has been mean centered.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.centeredCovariance'})
# Reducer.combine
# Creates a Reducer that runs two reducers in parallel.  The combined
# reducer's outputs will be those of reducer1 followed by those of reducer2,
# where the output names of reducer2 are prefixed with the given string. If
# sharedInputs is true, the reducers must have the same number of inputs, and
# the combined reducer's will match them; if it is false, the inputs of the
# combined reducer will be those of reducer1 followed by those of reducer2.
#
# Args:
#   reducer1
#   reducer2
#   outputPrefix: Prefix for reducer2's output names.
#   sharedInputs
signatures.append({'args': [{'name': 'reducer1', 'type': 'Reducer'}, {'name': 'reducer2', 'type': 'Reducer'}, {'default': '', 'description': "Prefix for reducer2's output names.", 'name': 'outputPrefix', 'optional': True, 'type': 'String'}, {'default': False, 'name': 'sharedInputs', 'optional': True, 'type': 'Boolean'}], 'description': "Creates a Reducer that runs two reducers in parallel.  The combined reducer's outputs will be those of reducer1 followed by those of reducer2, where the output names of reducer2 are prefixed with the given string.\nIf sharedInputs is true, the reducers must have the same number of inputs, and the combined reducer's will match them; if it is false, the inputs of the combined reducer will be those of reducer1 followed by those of reducer2.", 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.combine'})
# Reducer.count
# Returns a Reducer that computes the number of non-null inputs.
signatures.append({'args': [], 'description': 'Returns a Reducer that computes the number of non-null inputs.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.count'})
# Reducer.countDistinct
# Returns a Reducer that computes the number of distinct inputs.
signatures.append({'args': [], 'description': 'Returns a Reducer that computes the number of distinct inputs.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.countDistinct'})
# Reducer.countEvery
# Returns a Reducer that computes the number of inputs.
signatures.append({'args': [], 'description': 'Returns a Reducer that computes the number of inputs.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.countEvery'})
# Reducer.covariance
# Creates a reducer that reduces some number of 1-D arrays of the same length
# N to a covariance matrix of shape NxN.  This reducer uses the one-pass
# covariance formula from Sandia National Laboratories Technical Report
# SAND2008-6212, which can lose accuracy if the values span a large range.
signatures.append({'args': [], 'description': 'Creates a reducer that reduces some number of 1-D arrays of the same length N to a covariance matrix of shape NxN.  This reducer uses the one-pass covariance formula from Sandia National Laboratories Technical Report SAND2008-6212, which can lose accuracy if the values span a large range.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.covariance'})
# Reducer.disaggregate
# Separates aggregate inputs (Arrays, Lists or Dictionaries) into individual
# items that are then each passed to the specified reducer.  When used on
# dictionaries, the dictionary keys are ignored.  Non-aggregated inputs (ie:
# numbers or strings) are passed to the underlying reducer directly.
#
# Args:
#   reducer: The reducer for which to disaggregate inputs.
#   axis: If specified, indicates an array axis along which to
#       disaggregate.  If not specified, arrays are completely
#       disaggregated.  Ignored for non-array types.
signatures.append({'args': [{'description': 'The reducer for which to disaggregate inputs.', 'name': 'reducer', 'type': 'Reducer'}, {'default': None, 'description': 'If specified, indicates an array axis along which to disaggregate.  If not specified, arrays are completely disaggregated.  Ignored for non-array types.', 'name': 'axis', 'optional': True, 'type': 'Integer'}], 'description': 'Separates aggregate inputs (Arrays, Lists or Dictionaries) into individual items that are then each passed to the specified reducer.  When used on dictionaries, the dictionary keys are ignored.  Non-aggregated inputs (ie: numbers or strings) are passed to the underlying reducer directly.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.disaggregate'})
# Reducer.first
# Returns a Reducer that returns the first of its inputs.
signatures.append({'args': [], 'description': 'Returns a Reducer that returns the first of its inputs.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.first'})
# Reducer.firstNonNull
# Returns a Reducer that returns the first of its non-null inputs.
signatures.append({'args': [], 'description': 'Returns a Reducer that returns the first of its non-null inputs.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.firstNonNull'})
# Reducer.fixedHistogram
# Creates a reducer that will compute a histogram of the inputs using a fixed
# number of fixed width bins. Values outside of the [min, max) range are
# ignored.  The output is a Nx2 array of bucket lower edges and counts and is
# suitable for use per-pixel.
#
# Args:
#   min: The lower (inclusive) bound of the first bucket.
#   max: The upper (exclusive) bound of the last bucket.
#   steps: The number of buckets to use.
signatures.append({'args': [{'description': 'The lower (inclusive) bound of the first bucket.', 'name': 'min', 'type': 'Float'}, {'description': 'The upper (exclusive) bound of the last bucket.', 'name': 'max', 'type': 'Float'}, {'description': 'The number of buckets to use.', 'name': 'steps', 'type': 'Integer'}], 'description': 'Creates a reducer that will compute a histogram of the inputs using a fixed number of fixed width bins. Values outside of the [min, max) range are ignored.  The output is a Nx2 array of bucket lower edges and counts and is suitable for use per-pixel.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.fixedHistogram'})
# Reducer.forEach
# Creates a Reducer by combining a copy of the given reducer for each output
# name in the given list.  If the reducer has a single output, the output
# names are used as-is; otherwise they are prefixed to the original output
# names.
#
# Args:
#   reducer
#   outputNames
signatures.append({'args': [{'name': 'reducer', 'type': 'Reducer'}, {'name': 'outputNames', 'type': 'List'}], 'description': 'Creates a Reducer by combining a copy of the given reducer for each output name in the given list.  If the reducer has a single output, the output names are used as-is; otherwise they are prefixed to the original output names.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.forEach'})
# Reducer.forEachBand
# Creates a Reducer by combining a copy of the given reducer for each band in
# the given image, using the band names as output names.
#
# Args:
#   reducer
#   image
signatures.append({'args': [{'name': 'reducer', 'type': 'Reducer'}, {'name': 'image', 'type': 'Image'}], 'description': 'Creates a Reducer by combining a copy of the given reducer for each band in the given image, using the band names as output names.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.forEachBand'})
# Reducer.forEachElement
# Separately reduces each position in array inputs of equal shape, producing
# an array output of the same shape. For example, with the 'sum' reducer
# applied to 5 arrays with shape 2x2, the output will be a 2x2 array, where
# each position is the sum of the 5 values at that position.
#
# Args:
#   reducer: The reducer to apply to each array element.
signatures.append({'args': [{'description': 'The reducer to apply to each array element.', 'name': 'reducer', 'type': 'Reducer'}], 'description': "Separately reduces each position in array inputs of equal shape, producing an array output of the same shape.\nFor example, with the 'sum' reducer applied to 5 arrays with shape 2x2, the output will be a 2x2 array, where each position is the sum of the 5 values at that position.", 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.forEachElement'})
# Reducer.frequencyHistogram
# Returns a Reducer that returns a (weighted) frequency table of its inputs.
signatures.append({'args': [], 'description': 'Returns a Reducer that returns a (weighted) frequency table of its inputs.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.frequencyHistogram'})
# Reducer.getOutputs
# Returns a list of the output names of the given reducer.
#
# Args:
#   reducer
signatures.append({'args': [{'name': 'reducer', 'type': 'Reducer'}], 'description': 'Returns a list of the output names of the given reducer.', 'returns': 'List', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.getOutputs'})
# Reducer.group
# Groups reducer records by the value of a given input, and reduces each
# group with the given reducer.
#
# Args:
#   reducer: The reducer to apply to each group, without the group
#       field.
#   groupField: The field that contains record groups.
#   groupName: The dictionary key that contains the group.
#       Defaults to 'group'.
signatures.append({'args': [{'description': 'The reducer to apply to each group, without the group field.', 'name': 'reducer', 'type': 'Reducer'}, {'default': 0, 'description': 'The field that contains record groups.', 'name': 'groupField', 'optional': True, 'type': 'Integer'}, {'default': 'group', 'description': "The dictionary key that contains the group. Defaults to 'group'.", 'name': 'groupName', 'optional': True, 'type': 'String'}], 'description': 'Groups reducer records by the value of a given input, and reduces each group with the given reducer.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.group'})
# Reducer.histogram
# Create a reducer that will compute a histogram of the inputs.
#
# Args:
#   maxBuckets: The maximum number of buckets to use when
#       building a histogram; will be rounded up to a power of
#       2.
#   minBucketWidth: The minimum histogram bucket width, or
#       null to allow any power of 2.
#   maxRaw: The number of values to accumulate before building the
#       initial histogram.
signatures.append({'args': [{'default': None, 'description': 'The maximum number of buckets to use when building a histogram; will be rounded up to a power of 2.', 'name': 'maxBuckets', 'optional': True, 'type': 'Integer'}, {'default': None, 'description': 'The minimum histogram bucket width, or null to allow any power of 2.', 'name': 'minBucketWidth', 'optional': True, 'type': 'Float'}, {'default': None, 'description': 'The number of values to accumulate before building the initial histogram.', 'name': 'maxRaw', 'optional': True, 'type': 'Integer'}], 'description': 'Create a reducer that will compute a histogram of the inputs.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.histogram'})
# Reducer.histogramCombiner
# Some doc
#
# Args:
#   maxBuckets: The number of buckets of the output histogram.
#       If null, the default is used.
#   minBucketWidth: The minimum bucket width of the output
#       histogram. If null, the default is used.
signatures.append({'args': [{'default': None, 'description': 'The number of buckets of the output histogram. If null, the default is used.', 'name': 'maxBuckets', 'optional': True, 'type': 'Integer'}, {'default': None, 'description': 'The minimum bucket width of the output histogram. If null, the default is used.', 'name': 'minBucketWidth', 'optional': True, 'type': 'Float'}], 'description': 'Some doc', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': True, 'name': 'Reducer.histogramCombiner'})
# Reducer.intervalMean
# Creates a Reducer to compute the mean of all inputs in the specified
# percentile range.  For small numbers of inputs (up to maxRaw) the mean will
# be computed directly; for larger numbers of inputs the mean will be derived
# from a histogram.
#
# Args:
#   minPercentile: The lower bound of the percentile range.
#   maxPercentile: The upper bound of the percentile range.
#   maxBuckets: The maximum number of buckets to use when
#       building a histogram; will be rounded up to a power of
#       2.
#   minBucketWidth: The minimum histogram bucket width, or
#       null to allow any power of 2.
#   maxRaw: The number of values to accumulate before building the
#       initial histogram.
signatures.append({'args': [{'description': 'The lower bound of the percentile range.', 'name': 'minPercentile', 'type': 'Float'}, {'description': 'The upper bound of the percentile range.', 'name': 'maxPercentile', 'type': 'Float'}, {'default': None, 'description': 'The maximum number of buckets to use when building a histogram; will be rounded up to a power of 2.', 'name': 'maxBuckets', 'optional': True, 'type': 'Integer'}, {'default': None, 'description': 'The minimum histogram bucket width, or null to allow any power of 2.', 'name': 'minBucketWidth', 'optional': True, 'type': 'Float'}, {'default': None, 'description': 'The number of values to accumulate before building the initial histogram.', 'name': 'maxRaw', 'optional': True, 'type': 'Integer'}], 'description': 'Creates a Reducer to compute the mean of all inputs in the specified percentile range.  For small numbers of inputs (up to maxRaw) the mean will be computed directly; for larger numbers of inputs the mean will be derived from a histogram.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.intervalMean'})
# Reducer.kendallsCorrelation
# Creates a reducer that computes the Kendall's Tau-b rank correlation and
# p-value on a two-sided test of H0: x and y are independent.  A positive tau
# value indicates an increasing trend; negative value indicates a decreasing
# trend. Currently the p-value test is disabled and only returns null.
#
# Args:
#   numInputs: The number of inputs to expect (1 or 2).  If 1 is
#       specified, automatically generates sequence numbers for
#       the x value (meaning there can be no ties).
signatures.append({'args': [{'default': 1, 'description': 'The number of inputs to expect (1 or 2).  If 1 is specified, automatically generates sequence numbers for the x value (meaning there can be no ties).', 'name': 'numInputs', 'optional': True, 'type': 'Integer'}], 'description': "Creates a reducer that computes the Kendall's Tau-b rank correlation and p-value on a two-sided test of H0: x and y are independent.  A positive tau value indicates an increasing trend; negative value indicates a decreasing trend. Currently the p-value test is disabled and only returns null.", 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.kendallsCorrelation'})
# Reducer.kurtosis
# Returns a Reducer that Computes the kurtosis of its inputs.
signatures.append({'args': [], 'description': 'Returns a Reducer that Computes the kurtosis of its inputs.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.kurtosis'})
# Reducer.last
# Returns a Reducer that returns the last of its inputs.
signatures.append({'args': [], 'description': 'Returns a Reducer that returns the last of its inputs.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.last'})
# Reducer.lastNonNull
# Returns a Reducer that returns the last of its non-null inputs.
signatures.append({'args': [], 'description': 'Returns a Reducer that returns the last of its non-null inputs.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.lastNonNull'})
# Reducer.linearFit
# Returns a Reducer that computes the slope and offset for a (weighted)
# linear regression of 2 inputs.
signatures.append({'args': [], 'description': 'Returns a Reducer that computes the slope and offset for a (weighted) linear regression of 2 inputs.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.linearFit'})
# Reducer.linearRegression
# Creates a reducer that computes a linear least squares regression with numX
# independent variables and numY dependent variables. Each input tuple will
# have values for the independent variables followed by the dependent
# variables. The first output is a coefficients array with dimensions (numX,
# numY); each column contains the coefficients for the corresponding
# dependent variable.  The second output is a vector of the root mean square
# of the residuals of each dependent variable.  Both outputs are null if the
# system is underdetermined, e.g. the number of inputs is less than or equal
# to numX.
#
# Args:
#   numX: The number of input dimensions.
#   numY: The number of output dimensions.
signatures.append({'args': [{'description': 'The number of input dimensions.', 'name': 'numX', 'type': 'Integer'}, {'default': 1, 'description': 'The number of output dimensions.', 'name': 'numY', 'optional': True, 'type': 'Integer'}], 'description': 'Creates a reducer that computes a linear least squares regression with numX independent variables and numY dependent variables.\nEach input tuple will have values for the independent variables followed by the dependent variables.\nThe first output is a coefficients array with dimensions (numX, numY); each column contains the coefficients for the corresponding dependent variable.  The second output is a vector of the root mean square of the residuals of each dependent variable.  Both outputs are null if the system is underdetermined, e.g. the number of inputs is less than or equal to numX.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.linearRegression'})
# Reducer.max
# Creates a reducer that outputs the maximum value of its (first) input.  If
# numInputs is greater than one, also outputs the corresponding values of the
# additional inputs.
#
# Args:
#   numInputs: The number of inputs.
signatures.append({'args': [{'default': 1, 'description': 'The number of inputs.', 'name': 'numInputs', 'optional': True, 'type': 'Integer'}], 'description': 'Creates a reducer that outputs the maximum value of its (first) input.  If numInputs is greater than one, also outputs the corresponding values of the additional inputs.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.max'})
# Reducer.mean
# Returns a Reducer that computes the (weighted) arithmetic mean of its
# inputs.
signatures.append({'args': [], 'description': 'Returns a Reducer that computes the (weighted) arithmetic mean of its inputs.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.mean'})
# Reducer.median
# Create a reducer that will compute the median of the inputs.  For small
# numbers of inputs (up to maxRaw) the median will be computed directly; for
# larger numbers of inputs the median will be derived from a histogram.
#
# Args:
#   maxBuckets: The maximum number of buckets to use when
#       building a histogram; will be rounded up to a power of
#       2.
#   minBucketWidth: The minimum histogram bucket width, or
#       null to allow any power of 2.
#   maxRaw: The number of values to accumulate before building the
#       initial histogram.
signatures.append({'args': [{'default': None, 'description': 'The maximum number of buckets to use when building a histogram; will be rounded up to a power of 2.', 'name': 'maxBuckets', 'optional': True, 'type': 'Integer'}, {'default': None, 'description': 'The minimum histogram bucket width, or null to allow any power of 2.', 'name': 'minBucketWidth', 'optional': True, 'type': 'Float'}, {'default': None, 'description': 'The number of values to accumulate before building the initial histogram.', 'name': 'maxRaw', 'optional': True, 'type': 'Integer'}], 'description': 'Create a reducer that will compute the median of the inputs.  For small numbers of inputs (up to maxRaw) the median will be computed directly; for larger numbers of inputs the median will be derived from a histogram.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.median'})
# Reducer.min
# Creates a reducer that outputs the minimum value of its (first) input.  If
# numInputs is greater than one, also outputs the corresponding values of the
# additional inputs.
#
# Args:
#   numInputs: The number of inputs.
signatures.append({'args': [{'default': 1, 'description': 'The number of inputs.', 'name': 'numInputs', 'optional': True, 'type': 'Integer'}], 'description': 'Creates a reducer that outputs the minimum value of its (first) input.  If numInputs is greater than one, also outputs the corresponding values of the additional inputs.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.min'})
# Reducer.minMax
# Returns a Reducer that computes the minimum and maximum of its inputs.
signatures.append({'args': [], 'description': 'Returns a Reducer that computes the minimum and maximum of its inputs.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.minMax'})
# Reducer.mode
# Create a reducer that will compute the mode of the inputs.  For small
# numbers of inputs (up to maxRaw) the mode will be computed directly; for
# larger numbers of inputs the mode will be derived from a histogram.
#
# Args:
#   maxBuckets: The maximum number of buckets to use when
#       building a histogram; will be rounded up to a power of
#       2.
#   minBucketWidth: The minimum histogram bucket width, or
#       null to allow any power of 2.
#   maxRaw: The number of values to accumulate before building the
#       initial histogram.
signatures.append({'args': [{'default': None, 'description': 'The maximum number of buckets to use when building a histogram; will be rounded up to a power of 2.', 'name': 'maxBuckets', 'optional': True, 'type': 'Integer'}, {'default': None, 'description': 'The minimum histogram bucket width, or null to allow any power of 2.', 'name': 'minBucketWidth', 'optional': True, 'type': 'Float'}, {'default': None, 'description': 'The number of values to accumulate before building the initial histogram.', 'name': 'maxRaw', 'optional': True, 'type': 'Integer'}], 'description': 'Create a reducer that will compute the mode of the inputs.  For small numbers of inputs (up to maxRaw) the mode will be computed directly; for larger numbers of inputs the mode will be derived from a histogram.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.mode'})
# Reducer.or
# Returns a Reducer that returns 1 if any of its inputs are non-zero, 0
# otherwise.
signatures.append({'args': [], 'description': 'Returns a Reducer that returns 1 if any of its inputs are non-zero, 0 otherwise.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'deprecated': 'Use Reducer.anyNonZero().', 'name': 'Reducer.or'})
# Reducer.pearsonsCorrelation
# Creates a two-input reducer that computes Pearson's product-moment
# correlation coefficient and the 2-sided p-value test for correlation = 0.
signatures.append({'args': [], 'description': "Creates a two-input reducer that computes Pearson's product-moment correlation coefficient and the 2-sided p-value test for correlation = 0.", 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.pearsonsCorrelation'})
# Reducer.percentile
# Create a reducer that will compute the specified percentiles, e.g. given
# [0, 50, 100] will produce outputs named 'p0', 'p50', and 'p100' with the
# min, median, and max respectively.  For small numbers of inputs (up to
# maxRaw) the percentiles will be computed directly; for larger numbers of
# inputs the percentiles will be derived from a histogram.
#
# Args:
#   percentiles: A list of numbers between 0 and 100.
#   outputNames: A list of names for the outputs, or null to
#       get default names.
#   maxBuckets: The maximum number of buckets to use when
#       building a histogram; will be rounded up to a power of
#       2.
#   minBucketWidth: The minimum histogram bucket width, or
#       null to allow any power of 2.
#   maxRaw: The number of values to accumulate before building the
#       initial histogram.
signatures.append({'args': [{'description': 'A list of numbers between 0 and 100.', 'name': 'percentiles', 'type': 'List'}, {'default': None, 'description': 'A list of names for the outputs, or null to get default names.', 'name': 'outputNames', 'optional': True, 'type': 'List'}, {'default': None, 'description': 'The maximum number of buckets to use when building a histogram; will be rounded up to a power of 2.', 'name': 'maxBuckets', 'optional': True, 'type': 'Integer'}, {'default': None, 'description': 'The minimum histogram bucket width, or null to allow any power of 2.', 'name': 'minBucketWidth', 'optional': True, 'type': 'Float'}, {'default': None, 'description': 'The number of values to accumulate before building the initial histogram.', 'name': 'maxRaw', 'optional': True, 'type': 'Integer'}], 'description': "Create a reducer that will compute the specified percentiles, e.g. given [0, 50, 100] will produce outputs named 'p0', 'p50', and 'p100' with the min, median, and max respectively.  For small numbers of inputs (up to maxRaw) the percentiles will be computed directly; for larger numbers of inputs the percentiles will be derived from a histogram.", 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.percentile'})
# Reducer.product
# Returns a Reducer that computes the product of its inputs.
signatures.append({'args': [], 'description': 'Returns a Reducer that computes the product of its inputs.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.product'})
# Reducer.repeat
# Creates a Reducer by combining the specified number of copies of the given
# reducer.  Output names are the same as the given reducer, but each is a
# list of the corresponding output from each of the reducers.
#
# Args:
#   reducer
#   count
signatures.append({'args': [{'name': 'reducer', 'type': 'Reducer'}, {'name': 'count', 'type': 'Integer'}], 'description': 'Creates a Reducer by combining the specified number of copies of the given reducer.  Output names are the same as the given reducer, but each is a list of the corresponding output from each of the reducers.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.repeat'})
# Reducer.robustLinearRegression
# Creates a reducer that computes a robust least squares regression with numX
# independent variables and numY dependent variables, using iteratively
# reweighted least squares with the Talwar cost function. A point is
# considered an outlier if the RMS of residuals is greater than beta. Each
# input tuple will have values for the independent variables followed by the
# dependent variables. The first output is a coefficients array with
# dimensions (numX, numY); each column contains the coefficients for the
# corresponding dependent variable.  The second is a vector of the root mean
# square of the residuals of each dependent variable.  Both outputs are null
# if the system is underdetermined, e.g. the number of inputs is less than
# numX.
#
# Args:
#   numX: The number of input dimensions.
#   numY: The number of output dimensions.
#   beta: Residual error outlier margin. If null, a default value
#       will be computed.
signatures.append({'args': [{'description': 'The number of input dimensions.', 'name': 'numX', 'type': 'Integer'}, {'default': 1, 'description': 'The number of output dimensions.', 'name': 'numY', 'optional': True, 'type': 'Integer'}, {'default': None, 'description': 'Residual error outlier margin. If null, a default value will be computed.', 'name': 'beta', 'optional': True, 'type': 'Float'}], 'description': 'Creates a reducer that computes a robust least squares regression with numX independent variables and numY dependent variables, using iteratively reweighted least squares with the Talwar cost function. A point is considered an outlier if the RMS of residuals is greater than beta.\nEach input tuple will have values for the independent variables followed by the dependent variables.\nThe first output is a coefficients array with dimensions (numX, numY); each column contains the coefficients for the corresponding dependent variable.  The second is a vector of the root mean square of the residuals of each dependent variable.  Both outputs are null if the system is underdetermined, e.g. the number of inputs is less than numX.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.robustLinearRegression'})
# Reducer.sampleStdDev
# Returns a Reducer that computes the sample standard deviation of its
# inputs.
signatures.append({'args': [], 'description': 'Returns a Reducer that computes the sample standard deviation of its inputs.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.sampleStdDev'})
# Reducer.sampleVariance
# Returns a Reducer that computes the sample variance of its inputs.
signatures.append({'args': [], 'description': 'Returns a Reducer that computes the sample variance of its inputs.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.sampleVariance'})
# Reducer.sensSlope
# Creates a two-input reducer that computes the Sen's slope estimator.  It
# returns two double values; the estimated slope and the offset.
signatures.append({'args': [], 'description': "Creates a two-input reducer that computes the Sen's slope estimator.  It returns two double values; the estimated slope and the offset.", 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.sensSlope'})
# Reducer.setOutputs
# Returns a Reducer with the same inputs as the given Reducer, but with
# outputs renamed and/or removed.
#
# Args:
#   reducer
#   outputs: The new output names; any output whose name is null
#       or empty will be dropped.
signatures.append({'args': [{'name': 'reducer', 'type': 'Reducer'}, {'description': 'The new output names; any output whose name is null or empty will be dropped.', 'name': 'outputs', 'type': 'List'}], 'description': 'Returns a Reducer with the same inputs as the given Reducer, but with outputs renamed and/or removed.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.setOutputs'})
# Reducer.skew
# Returns a Reducer that Computes the skewness of its inputs.
signatures.append({'args': [], 'description': 'Returns a Reducer that Computes the skewness of its inputs.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.skew'})
# Reducer.spearmansCorrelation
# Creates a two-input reducer that computes the Spearman's rank-moment
# correlation and its p-value on a two-sided test of H0: x and y are
# independent.  Currently, the p-value test is disabled and returns null.
signatures.append({'args': [], 'description': "Creates a two-input reducer that computes the Spearman's rank-moment correlation and its p-value on a two-sided test of H0: x and y are independent.  Currently, the p-value test is disabled and returns null.", 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.spearmansCorrelation'})
# Reducer.splitWeights
# Returns a Reducer with the same outputs as the given Reducer, but with each
# weighted input replaced by two unweighted inputs.
#
# Args:
#   reducer
signatures.append({'args': [{'name': 'reducer', 'type': 'Reducer'}], 'description': 'Returns a Reducer with the same outputs as the given Reducer, but with each weighted input replaced by two unweighted inputs.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.splitWeights'})
# Reducer.stdDev
# Returns a Reducer that computes the standard deviation of its inputs.
signatures.append({'args': [], 'description': 'Returns a Reducer that computes the standard deviation of its inputs.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.stdDev'})
# Reducer.sum
# Returns a Reducer that computes the (weighted) sum of its inputs.
signatures.append({'args': [], 'description': 'Returns a Reducer that computes the (weighted) sum of its inputs.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.sum'})
# Reducer.toCollection
# Returns a reducer that collects its inputs into a FeatureCollection.
#
# Args:
#   propertyNames: The property names that will be defined
#       on each output feature; determines the number of
#       reducer inputs.
#   numOptional: The last numOptional inputs will be
#       considered optional; the other inputs must be non-null
#       or the input tuple will be dropped.
signatures.append({'args': [{'description': 'The property names that will be defined on each output feature; determines the number of reducer inputs.', 'name': 'propertyNames', 'type': 'List'}, {'default': 0, 'description': 'The last numOptional inputs will be considered optional; the other inputs must be non-null or the input tuple will be dropped.', 'name': 'numOptional', 'optional': True, 'type': 'Integer'}], 'description': 'Returns a reducer that collects its inputs into a FeatureCollection.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.toCollection'})
# Reducer.toList
# Creates a reducer that collects its inputs into a list, optionally grouped
# into tuples.
#
# Args:
#   tupleSize: The size of each output tuple, or null for no
#       grouping. Also determines the number of inputs (null
#       tupleSize has 1 input).
#   numOptional: The last numOptional inputs will be
#       considered optional; the other inputs must be non-null
#       or the input tuple will be dropped.
signatures.append({'args': [{'default': None, 'description': 'The size of each output tuple, or null for no grouping. Also determines the number of inputs (null tupleSize has 1 input).', 'name': 'tupleSize', 'optional': True, 'type': 'Integer'}, {'default': 0, 'description': 'The last numOptional inputs will be considered optional; the other inputs must be non-null or the input tuple will be dropped.', 'name': 'numOptional', 'optional': True, 'type': 'Integer'}], 'description': 'Creates a reducer that collects its inputs into a list, optionally grouped into tuples.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.toList'})
# Reducer.unweighted
# Returns a Reducer with the same inputs and outputs as the given Reducer,
# but with no weighted inputs.
#
# Args:
#   reducer
signatures.append({'args': [{'name': 'reducer', 'type': 'Reducer'}], 'description': 'Returns a Reducer with the same inputs and outputs as the given Reducer, but with no weighted inputs.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.unweighted'})
# Reducer.variance
# Returns a Reducer that computes the variance of its inputs.
signatures.append({'args': [], 'description': 'Returns a Reducer that computes the variance of its inputs.', 'returns': 'Reducer', 'type': 'Algorithm', 'hidden': False, 'name': 'Reducer.variance'})
# S1.dB
# Computes Sentinel 1 decibel values from the stored raw UINT16 image. Also
# applies bicubic interpolation to the incidence angle band.
#
# Args:
#   image: The raw Sentinel 1 UINT16 image.
signatures.append({'args': [{'description': 'The raw Sentinel 1 UINT16 image.', 'name': 'image', 'type': 'Image'}], 'description': 'Computes Sentinel 1 decibel values from the stored raw UINT16 image. Also applies bicubic interpolation to the incidence angle band.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': True, 'name': 'S1.dB'})
# SampleImage.AggregationContainer
# INTERNAL
#
# Args:
#   image
#   proj
#   region
#   factor
#   seed
#   dropNulls
#   tileScale
signatures.append({'args': [{'name': 'image', 'type': 'Image'}, {'name': 'proj', 'type': 'Projection'}, {'name': 'region', 'type': 'Geometry'}, {'name': 'factor', 'type': 'Float'}, {'name': 'seed', 'type': 'Long'}, {'name': 'dropNulls', 'type': 'Boolean'}, {'name': 'tileScale', 'type': 'Float'}], 'description': 'INTERNAL', 'returns': 'Image', 'type': 'Algorithm', 'hidden': True, 'name': 'SampleImage.AggregationContainer'})
# SelectorSet
# Returns a SelectorSet for a list of selector paths.
#
# Args:
#   paths
signatures.append({'args': [{'name': 'paths', 'type': 'Object'}], 'description': 'Returns a SelectorSet for a list of selector paths.', 'returns': 'SelectorSet', 'type': 'Algorithm', 'hidden': False, 'name': 'SelectorSet'})
# SelectorSet.Geometry
# Returns a geometry SelectorSet for a given error margin and region.
#
# Args:
#   errorMeters
#   region
signatures.append({'args': [{'name': 'errorMeters', 'type': 'Float'}, {'name': 'region', 'type': 'Rectangle'}], 'description': 'Returns a geometry SelectorSet for a given error margin and region.', 'returns': 'SelectorSet', 'type': 'Algorithm', 'hidden': True, 'name': 'SelectorSet.Geometry'})
# SelectorSet.Object
# Returns a SelectorSet for a given set of property paths.
#
# Args:
#   map
signatures.append({'args': [{'name': 'map', 'type': 'Dictionary'}], 'description': 'Returns a SelectorSet for a given set of property paths.', 'returns': 'SelectorSet', 'type': 'Algorithm', 'hidden': True, 'name': 'SelectorSet.Object'})
# SelectorSet.Simple
# Returns a SelectorSet for either the whole object or nothing.
#
# Args:
#   all
signatures.append({'args': [{'name': 'all', 'type': 'Boolean'}], 'description': 'Returns a SelectorSet for either the whole object or nothing.', 'returns': 'SelectorSet', 'type': 'Algorithm', 'hidden': True, 'name': 'SelectorSet.Simple'})
# StratifiedSampleImage.AggregationContainer
# INTERNAL
#
# Args:
#   image
#   classIndex
#   proj
#   region
#   numPixels
#   classValues
#   classPoints
#   dropNulls
#   seed
#   tileScale
signatures.append({'args': [{'name': 'image', 'type': 'Image'}, {'name': 'classIndex', 'type': 'Integer'}, {'name': 'proj', 'type': 'Projection'}, {'name': 'region', 'type': 'Geometry'}, {'name': 'numPixels', 'type': 'Integer'}, {'name': 'classValues', 'type': 'List'}, {'name': 'classPoints', 'type': 'List'}, {'name': 'dropNulls', 'type': 'Boolean'}, {'name': 'seed', 'type': 'Long'}, {'name': 'tileScale', 'type': 'Float'}], 'description': 'INTERNAL', 'returns': 'Image', 'type': 'Algorithm', 'hidden': True, 'name': 'StratifiedSampleImage.AggregationContainer'})
# String
# Converts the input to a string.
#
# Args:
#   input: The object to convert.
signatures.append({'args': [{'description': 'The object to convert.', 'name': 'input', 'type': 'Object'}], 'description': 'Converts the input to a string.', 'returns': 'String', 'type': 'Algorithm', 'hidden': False, 'name': 'String'})
# String.cat
# Concatenates two strings.
#
# Args:
#   string1: The first string.
#   string2: The second string.
signatures.append({'args': [{'description': 'The first string.', 'name': 'string1', 'type': 'String'}, {'description': 'The second string.', 'name': 'string2', 'type': 'String'}], 'description': 'Concatenates two strings.', 'returns': 'String', 'type': 'Algorithm', 'hidden': False, 'name': 'String.cat'})
# String.compareTo
# Compares two strings lexicographically. Returns: the value 0 if the two
# strings are lexicographically equal; a value less than 0 if string1 is less
# than string2;  and a value greater than 0 if string1 is lexicographically
# greater than string2.
#
# Args:
#   string1: The string to compare.
#   string2: The string to be compared.
signatures.append({'args': [{'description': 'The string to compare.', 'name': 'string1', 'type': 'String'}, {'description': 'The string to be compared.', 'name': 'string2', 'type': 'String'}], 'description': 'Compares two strings lexicographically. Returns: the value 0 if the two strings are lexicographically equal; a value less than 0 if string1 is less than string2;  and a value greater than 0 if string1 is lexicographically greater than string2. ', 'returns': 'Integer', 'type': 'Algorithm', 'hidden': False, 'name': 'String.compareTo'})
# String.decodeJSON
# Decodes a JSON string.
#
# Args:
#   string: The string to decode.
signatures.append({'args': [{'description': 'The string to decode.', 'name': 'string', 'type': 'String'}], 'description': 'Decodes a JSON string.', 'returns': 'Object', 'type': 'Algorithm', 'hidden': False, 'name': 'String.decodeJSON'})
# String.index
# Searches a string for the first occurrence of a substring.  Returns the
# index of the first match, or -1.
#
# Args:
#   target: The string to search.
#   pattern: The string to find.
signatures.append({'args': [{'description': 'The string to search.', 'name': 'target', 'type': 'String'}, {'description': 'The string to find.', 'name': 'pattern', 'type': 'String'}], 'description': 'Searches a string for the first occurrence of a substring.  Returns the index of the first match, or -1.', 'returns': 'Integer', 'type': 'Algorithm', 'hidden': False, 'name': 'String.index'})
# String.length
# Returns the length of a string.
#
# Args:
#   string: The string from which to get the length.
signatures.append({'args': [{'description': 'The string from which to get the length.', 'name': 'string', 'type': 'String'}], 'description': 'Returns the length of a string.', 'returns': 'Integer', 'type': 'Algorithm', 'hidden': False, 'name': 'String.length'})
# String.match
# Matches a string against a regular expression.  Returns a list of matching
# strings.
#
# Args:
#   input: The string in which to search.
#   regex: The regular expression to match.
#   flags: A string specifying a combination of regular expression
#       flags, specifically one or more of: 'g' (global match) or
#       'i' (ignore case)
signatures.append({'args': [{'description': 'The string in which to search.', 'name': 'input', 'type': 'String'}, {'description': 'The regular expression to match.', 'name': 'regex', 'type': 'String'}, {'default': '', 'description': "A string specifying a combination of regular expression flags, specifically one or more of: 'g' (global match) or 'i' (ignore case)", 'name': 'flags', 'optional': True, 'type': 'String'}], 'description': 'Matches a string against a regular expression.  Returns a list of matching strings.', 'returns': 'List', 'type': 'Algorithm', 'hidden': False, 'name': 'String.match'})
# String.replace
# Returns a new string with some or all matches of a pattern replaced.
#
# Args:
#   input: The string in which to search.
#   regex: The regular expression to match.
#   replacement: The string that replaces the matched
#       substring.
#   flags: A string specifying a combination of regular expression
#       flags, specifically one or more of: 'g' (global match) or
#       'i' (ignore case)
signatures.append({'args': [{'description': 'The string in which to search.', 'name': 'input', 'type': 'String'}, {'description': 'The regular expression to match.', 'name': 'regex', 'type': 'String'}, {'description': 'The string that replaces the matched substring.', 'name': 'replacement', 'type': 'String'}, {'default': '', 'description': "A string specifying a combination of regular expression flags, specifically one or more of: 'g' (global match) or 'i' (ignore case)", 'name': 'flags', 'optional': True, 'type': 'String'}], 'description': 'Returns a new string with some or all matches of a pattern replaced.', 'returns': 'String', 'type': 'Algorithm', 'hidden': False, 'name': 'String.replace'})
# String.rindex
# Searches a string for the last occurrence of a substring.  Returns the
# index of the first match, or -1.
#
# Args:
#   target: The string to search.
#   pattern: The string to find.
signatures.append({'args': [{'description': 'The string to search.', 'name': 'target', 'type': 'String'}, {'description': 'The string to find.', 'name': 'pattern', 'type': 'String'}], 'description': 'Searches a string for the last occurrence of a substring.  Returns the index of the first match, or -1.', 'returns': 'Integer', 'type': 'Algorithm', 'hidden': False, 'name': 'String.rindex'})
# String.slice
# Returns a substring of the given string. If the specified range exceeds the
# length of the string, returns a shorter substring.
#
# Args:
#   string: The string to subset.
#   start: The beginning index, inclusive.  Negative numbers count
#       backwards from the end of the string.
#   end: The ending index, exclusive.  Defaults to the length of the
#       string. Negative numbers count backwards from the end of the
#       string.
signatures.append({'args': [{'description': 'The string to subset.', 'name': 'string', 'type': 'String'}, {'description': 'The beginning index, inclusive.  Negative numbers count backwards from the end of the string.', 'name': 'start', 'type': 'Integer'}, {'default': None, 'description': 'The ending index, exclusive.  Defaults to the length of the string. Negative numbers count backwards from the end of the string.', 'name': 'end', 'optional': True, 'type': 'Integer'}], 'description': 'Returns a substring of the given string. If the specified range exceeds the length of the string, returns a shorter substring.', 'returns': 'String', 'type': 'Algorithm', 'hidden': False, 'name': 'String.slice'})
# String.split
# Splits a string on a regular expression, Returning a list of strings.
#
# Args:
#   string: The string to split.
#   regex: A regular expression to split on. If regex is the empty
#       string, then the input string is split into individual
#       characters.
#   flags: A string specifying the regular expression flag: 'i'
#       (ignore case)
signatures.append({'args': [{'description': 'The string to split.', 'name': 'string', 'type': 'String'}, {'description': 'A regular expression to split on. If regex is the empty string, then the input string is split into individual characters.', 'name': 'regex', 'type': 'String'}, {'default': '', 'description': "A string specifying the regular expression flag: 'i' (ignore case)", 'name': 'flags', 'optional': True, 'type': 'String'}], 'description': 'Splits a string on a regular expression, Returning a list of strings.', 'returns': 'List', 'type': 'Algorithm', 'hidden': False, 'name': 'String.split'})
# String.toLowerCase
# Converts all of the characters in a string to lower case.
#
# Args:
#   string: The string to convert to lower case.
signatures.append({'args': [{'description': 'The string to convert to lower case.', 'name': 'string', 'type': 'String'}], 'description': 'Converts all of the characters in a string to lower case.', 'returns': 'String', 'type': 'Algorithm', 'hidden': False, 'name': 'String.toLowerCase'})
# String.toUpperCase
# Converts all of the characters in a string to upper case.
#
# Args:
#   string: The string to convert to upper case.
signatures.append({'args': [{'description': 'The string to convert to upper case.', 'name': 'string', 'type': 'String'}], 'description': 'Converts all of the characters in a string to upper case.', 'returns': 'String', 'type': 'Algorithm', 'hidden': False, 'name': 'String.toUpperCase'})
# String.trim
# Returns a string whose value is the original string, with any leading and
# trailing whitespace removed.
#
# Args:
#   string: The string to trim.
signatures.append({'args': [{'description': 'The string to trim.', 'name': 'string', 'type': 'String'}], 'description': 'Returns a string whose value is the original string, with any leading and trailing whitespace removed.', 'returns': 'String', 'type': 'Algorithm', 'hidden': False, 'name': 'String.trim'})
# TemporalSegmentation.Ewmacd
# Exponentially Weighted Moving Average Change Detection. This algorithm
# computes a harmonic model for the 'training' portion of the input data and
# subtracts that from the original results.  The residuals are then subjected
# to Shewhart X-bar charts and an exponentially weighted moving average.
# Disturbed pixels are indicated when the charts signal a deviation from the
# given control limits.  The output is a 5 band image containining the bands:
# ewma: a 1D array of the EWMA score for each input image. Negative values
# represent disturbance and positive values represent recovery.
# harmonicCoefficients: A 1-D array of the computed harmonic coefficient
# pairs. The coefficients are ordered as [constant, sin0, cos0, sin1,
# cos1...]     rmse: the RMSE from the harmonic regression.     rSquared:
# r-squared value from the harmonic regression.     residuals: 1D array of
# residuals from the harmonic regression. See: Brooks, E.B., Wynne, R.H.,
# Thomas, V.A., Blinn, C.E. and Coulston, J.W., 2014. On-the-fly massively
# multitemporal change detection using statistical quality control charts and
# Landsat data. IEEE Transactions on Geoscience and Remote Sensing, 52(6),
# pp.3316-3332.
#
# Args:
#   timeSeries: Collection from which to extract EWMA. This
#       collection is expected to contain 1 image for each year
#       and be sorted temporally.
#   vegetationThreshold: Threshold for vegetation.
#       Values below this are considered non-
#       vegetation.
#   trainingStartYear: Start year of training period,
#       inclusive.
#   trainingEndYear: End year of training period,
#       exclusive.
#   harmonicCount: Number of harmonic function pairs (sine
#       and cosine) used.
#   xBarLimit1: Threshold for initial training xBar limit.
#   xBarLimit2: Threshold for running xBar limit.
#   lambda: The 'lambda' tuning parameter weighting new years vs
#       the running average.
#   lambdasigs: EWMA control bounds, in units of standard
#       deviations.
#   rounding: Should rounding be performed for EWMA
#   persistence: Minimum number of observations needed to
#       consider a change.
signatures.append({'args': [{'description': 'Collection from which to extract EWMA. This collection is expected to contain 1 image for each year and be sorted temporally.', 'name': 'timeSeries', 'type': 'ImageCollection'}, {'description': 'Threshold for vegetation. Values below this are considered non-vegetation.', 'name': 'vegetationThreshold', 'type': 'Float'}, {'description': 'Start year of training period, inclusive.', 'name': 'trainingStartYear', 'type': 'Integer'}, {'description': 'End year of training period, exclusive.', 'name': 'trainingEndYear', 'type': 'Integer'}, {'default': 2, 'description': 'Number of harmonic function pairs (sine and cosine) used.', 'name': 'harmonicCount', 'optional': True, 'type': 'Integer'}, {'default': 1.5, 'description': 'Threshold for initial training xBar limit.', 'name': 'xBarLimit1', 'optional': True, 'type': 'Float'}, {'default': 20, 'description': 'Threshold for running xBar limit.', 'name': 'xBarLimit2', 'optional': True, 'type': 'Integer'}, {'default': 0.3, 'description': "The 'lambda' tuning parameter weighting new years vs the running average.", 'name': 'lambda', 'optional': True, 'type': 'Float'}, {'default': 3.0, 'description': 'EWMA control bounds, in units of standard deviations.', 'name': 'lambdasigs', 'optional': True, 'type': 'Float'}, {'default': True, 'description': 'Should rounding be performed for EWMA', 'name': 'rounding', 'optional': True, 'type': 'Boolean'}, {'default': 3, 'description': 'Minimum number of observations needed to consider a change.', 'name': 'persistence', 'optional': True, 'type': 'Integer'}], 'description': "Exponentially Weighted Moving Average Change Detection. This algorithm computes a harmonic model for the 'training' portion of the input data and subtracts that from the original results.  The residuals are then subjected to Shewhart X-bar charts and an exponentially weighted moving average.  Disturbed pixels are indicated when the charts signal a deviation from the given control limits.\n The output is a 5 band image containining the bands:\n    ewma: a 1D array of the EWMA score for each input image. Negative values represent disturbance and positive values represent recovery.\n    harmonicCoefficients: A 1-D array of the computed harmonic coefficient pairs. The coefficients are ordered as [constant, sin0, cos0, sin1, cos1...]\n    rmse: the RMSE from the harmonic regression.\n    rSquared: r-squared value from the harmonic regression.\n    residuals: 1D array of residuals from the harmonic regression.\nSee: Brooks, E.B., Wynne, R.H., Thomas, V.A., Blinn, C.E. and Coulston, J.W., 2014. On-the-fly massively multitemporal change detection using statistical quality control charts and Landsat data. IEEE Transactions on Geoscience and Remote Sensing, 52(6), pp.3316-3332.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'TemporalSegmentation.Ewmacd'})
# TemporalSegmentation.LandTrendr
# Landsat-based detection of Trends in Disturbance and Recovery: temporally
# segments a time-series of images by extracting the spectral trajectories of
# change over time. The first band of each image is used to find breakpoints,
# and those breakpoints are used to perform fitting on all subsequent bands.
# The breakpoints are returned as a 2-D matrix of 4 rows and as many columns
# as images. The first two rows are the original X and Y values. The third
# row contains the Y values fitted to the estimated segments, and the 4th row
# contains a 1 if the corresponding point was used as a segment vertex or 0
# if not. Any additional fitted bands are appended as rows in the output.
# Breakpoint fitting assumes that increasing values represent disturbance and
# decreasing values represent recovery. See: Kennedy, R.E., Yang, Z. and
# Cohen, W.B., 2010. Detecting trends in forest disturbance and recovery
# using yearly Landsat time series: 1. LandTrendr - Temporal segmentation
# algorithms. Remote Sensing of Environment, 114(12), pp.2897-2910.
#
# Args:
#   timeSeries: Yearly time-series from which to extract
#       breakpoints. The first band is usedto find breakpoints,
#       and all subsequent bands are fitted using those
#       breakpoints.
#   maxSegments: Maximum number of segments to be fitted on
#       the time series.
#   spikeThreshold: Threshold for dampening the spikes (1.0
#       means no dampening).
#   vertexCountOvershoot: The initial model can
#       overshoot the maxSegments + 1 vertices by
#       this amount. Later, it will be pruned down to
#       maxSegments + 1.
#   preventOneYearRecovery: Prevent segments that
#       represent one year recoveries.
#   recoveryThreshold: If a segment has a recovery rate
#       faster than 1/recoveryThreshold (in years), then
#       the segment is disallowed.
#   pvalThreshold: If the p-value of the fitted model
#       exceeds this threshold, then the current model is
#       discarded and another one is fitted using the
#       Levenberg-Marquardt optimizer.
#   bestModelProportion: Takes the model with most
#       vertices that has a p-value that is at most
#       this proportion away from the model with
#       lowest p-value.
#   minObservationsNeeded: Min observations needed
#       to perform output fitting.
signatures.append({'args': [{'description': 'Yearly time-series from which to extract breakpoints. The first band is usedto find breakpoints, and all subsequent bands are fitted using those breakpoints.', 'name': 'timeSeries', 'type': 'ImageCollection'}, {'description': 'Maximum number of segments to be fitted on the time series.', 'name': 'maxSegments', 'type': 'Integer'}, {'default': 0.9, 'description': 'Threshold for dampening the spikes (1.0 means no dampening).', 'name': 'spikeThreshold', 'optional': True, 'type': 'Float'}, {'default': 3, 'description': 'The initial model can overshoot the maxSegments + 1 vertices by this amount. Later, it will be pruned down to maxSegments + 1.', 'name': 'vertexCountOvershoot', 'optional': True, 'type': 'Integer'}, {'default': False, 'description': 'Prevent segments that represent one year recoveries.', 'name': 'preventOneYearRecovery', 'optional': True, 'type': 'Boolean'}, {'default': 0.25, 'description': 'If a segment has a recovery rate faster than 1/recoveryThreshold (in years), then the segment is disallowed.', 'name': 'recoveryThreshold', 'optional': True, 'type': 'Float'}, {'default': 0.1, 'description': 'If the p-value of the fitted model exceeds this threshold, then the current model is discarded and another one is fitted using the Levenberg-Marquardt optimizer.', 'name': 'pvalThreshold', 'optional': True, 'type': 'Float'}, {'default': 1.25, 'description': 'Takes the model with most vertices that has a p-value that is at most this proportion away from the model with lowest p-value.', 'name': 'bestModelProportion', 'optional': True, 'type': 'Float'}, {'default': 6, 'description': 'Min observations needed to perform output fitting.', 'name': 'minObservationsNeeded', 'optional': True, 'type': 'Integer'}], 'description': 'Landsat-based detection of Trends in Disturbance and Recovery: temporally segments a time-series of images by extracting the spectral trajectories of change over time. The first band of each image is used to find breakpoints, and those breakpoints are used to perform fitting on all subsequent bands. The breakpoints are returned as a 2-D matrix of 4 rows and as many columns as images. The first two rows are the original X and Y values. The third row contains the Y values fitted to the estimated segments, and the 4th row contains a 1 if the corresponding point was used as a segment vertex or 0 if not. Any additional fitted bands are appended as rows in the output. Breakpoint fitting assumes that increasing values represent disturbance and decreasing values represent recovery.\nSee: Kennedy, R.E., Yang, Z. and Cohen, W.B., 2010. Detecting trends in forest disturbance and recovery using yearly Landsat time series: 1. LandTrendr - Temporal segmentation algorithms. Remote Sensing of Environment, 114(12), pp.2897-2910.\n', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'TemporalSegmentation.LandTrendr'})
# TemporalSegmentation.LandTrendrFit
# Interpolates a time series using a set of LandTrendr breakpoint years. For
# each input band in the timeSeries, outputs a new 1D array-valued band
# containing the input values interpolated between the breakpoint times
# identified by the vertices image.  See the LandTrendr Algorithm for more
# details.
#
# Args:
#   timeSeries: Time series to interpolate.
#   vertices: Vertices image. A 1D array of LandTrendr breakpoint
#       years.
#   spikeThreshold: Threshold for dampening input spikes
#       (1.0 means no dampening).
#   minObservationsNeeded: Min observations needed.
signatures.append({'args': [{'description': 'Time series to interpolate.', 'name': 'timeSeries', 'type': 'ImageCollection'}, {'description': 'Vertices image. A 1D array of LandTrendr breakpoint years.', 'name': 'vertices', 'type': 'Image'}, {'default': 0.9, 'description': 'Threshold for dampening input spikes (1.0 means no dampening).', 'name': 'spikeThreshold', 'optional': True, 'type': 'Float'}, {'default': 6, 'description': 'Min observations needed.', 'name': 'minObservationsNeeded', 'optional': True, 'type': 'Integer'}], 'description': 'Interpolates a time series using a set of LandTrendr breakpoint years. For each input band in the timeSeries, outputs a new 1D array-valued band containing the input values interpolated between the breakpoint times identified by the vertices image.  See the LandTrendr Algorithm for more details.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'TemporalSegmentation.LandTrendrFit'})
# TemporalSegmentation.VCT
# Vegetation Change Tracker, an automated approach for reconstructing recent
# forest disturbance history using dense Landsat time series stacks. The
# output is a 2D array per pixel containing 6 rows x N years.  The output
# rows contain: input years, VCT landcover mask, magnitude in term of the UD
# composite, magnitude of distubance in B4, magnitude of distubance in NDVI,
# magnitude of distubance in dNBR. See: Huang, C., Goward, S.N., Masek, J.G.,
# Thomas, N., Zhu, Z. and Vogelmann, J.E., 2010. An automated approach for
# reconstructing recent forest disturbance history using dense Landsat time
# series stacks. Remote Sensing of Environment, 114(1), pp.183-198.
#
# Args:
#   timeSeries: Collection from which to extract VCT
#       disturbances, containing the bands: B3, B4, B5, B7,
#       thermal, NDVI, DNBR and COMP.  This collection is
#       expected to contain 1 image for each year, sorted by
#       time.
#   landCover: Collection from which to extract VCT masks. This
#       collection is expected to contain 1 image for each image
#       in the timeSeries, sorted by time.
#   maxUd: Maximum Z-score composite value for detecting forest.
#   minNdvi: Minimum NDVI value for forest.
#   forThrMax: Maximum threshold for forest.
#   nYears: Maximum number of years.
signatures.append({'args': [{'description': 'Collection from which to extract VCT disturbances, containing the bands: B3, B4, B5, B7, thermal, NDVI, DNBR and COMP.  This collection is expected to contain 1 image for each year, sorted by time.', 'name': 'timeSeries', 'type': 'ImageCollection'}, {'description': 'Collection from which to extract VCT masks. This collection is expected to contain 1 image for each image in the timeSeries, sorted by time.', 'name': 'landCover', 'type': 'ImageCollection'}, {'default': 4.0, 'description': 'Maximum Z-score composite value for detecting forest.', 'name': 'maxUd', 'optional': True, 'type': 'Float'}, {'default': 0.45, 'description': 'Minimum NDVI value for forest.', 'name': 'minNdvi', 'optional': True, 'type': 'Float'}, {'default': 3.0, 'description': 'Maximum threshold for forest.', 'name': 'forThrMax', 'optional': True, 'type': 'Float'}, {'default': 30, 'description': 'Maximum number of years.', 'name': 'nYears', 'optional': True, 'type': 'Integer'}], 'description': 'Vegetation Change Tracker, an automated approach for reconstructing recent forest disturbance history using dense Landsat time series stacks.\nThe output is a 2D array per pixel containing 6 rows x N years.  The output rows contain: input years, VCT landcover mask, magnitude in term of the UD composite, magnitude of distubance in B4, magnitude of distubance in NDVI, magnitude of distubance in dNBR.\nSee: Huang, C., Goward, S.N., Masek, J.G., Thomas, N., Zhu, Z. and Vogelmann, J.E., 2010. An automated approach for reconstructing recent forest disturbance history using dense Landsat time series stacks. Remote Sensing of Environment, 114(1), pp.183-198.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'TemporalSegmentation.VCT'})
# TemporalSegmentation.Verdet
# Vegetation Regeneration and Disturbance Estimates through Time, forest
# change detection algorithm. This algorithm generates a yearly clear-sky
# composite from satellite imagery, calculates a spectral vegetation index
# for each pixel in that composite, spatially segments the vegetation index
# image into patches, temporally divides the time series into differently
# sloped segments, and then labels those segments as disturbed, stable, or
# regenerating. Segmentation at both the spatial and temporal steps are
# performed using total variation regularization. The output consists of a 1D
# array per pixel containing the slope of fitted trend lines. Negative values
# indicate disturbance and positive values regeneration. See: Hughes, M.J.,
# Kaylor, S.D. and Hayes, D.J., 2017.  Patch-based forest change detection
# from Landsat time series. Forests, 8(5), p.166.
#
# Args:
#   timeSeries: Collection from which to extract VeRDET scores.
#       This collection is expected to contain 1 image for each
#       year, sorted temporally.
#   tolerance: convergence tolerance
#   alpha: Regularization parameter for segmentation.
#   nRuns: Maximum number of runs for convergence.
signatures.append({'args': [{'description': 'Collection from which to extract VeRDET scores. This collection is expected to contain 1 image for each year, sorted temporally.', 'name': 'timeSeries', 'type': 'ImageCollection'}, {'default': 0.0001, 'description': 'convergence tolerance', 'name': 'tolerance', 'optional': True, 'type': 'Float'}, {'default': 0.03333333333333333, 'description': 'Regularization parameter for segmentation.', 'name': 'alpha', 'optional': True, 'type': 'Float'}, {'default': 100, 'description': 'Maximum number of runs for convergence.', 'name': 'nRuns', 'optional': True, 'type': 'Integer'}], 'description': 'Vegetation Regeneration and Disturbance Estimates through Time, forest change detection algorithm. This algorithm generates a yearly clear-sky composite from satellite imagery, calculates a spectral vegetation index for each pixel in that composite, spatially segments the vegetation index image into patches, temporally divides the time series into differently sloped segments, and then labels those segments as disturbed, stable, or regenerating. Segmentation at both the spatial and temporal steps are performed using total variation regularization.\nThe output consists of a 1D array per pixel containing the slope of fitted trend lines. Negative values indicate disturbance and positive values regeneration.\nSee: Hughes, M.J., Kaylor, S.D. and Hayes, D.J., 2017.  Patch-based forest change detection from Landsat time series. Forests, 8(5), p.166.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'TemporalSegmentation.Verdet'})
# Terrain
# Calculates slope, aspect, and a simple hillshade from a terrain DEM.
# Expects an image containing either a single band of elevation, measured in
# meters, or if there's more than one band, one named 'elevation'. Adds
# output bands named 'slope' and 'aspect' measured in degrees plus an
# unsigned byte output band named 'hillshade' for visualization. All other
# bands and metadata are copied from the input image. The local gradient is
# computed using the 4-connected neighbors of each pixel, so missing values
# will occur around the edges of an image.
#
# Args:
#   input: An elevation image, in meters.
signatures.append({'args': [{'description': 'An elevation image, in meters.', 'name': 'input', 'type': 'Image'}], 'description': "Calculates slope, aspect, and a simple hillshade from a terrain DEM.\n\nExpects an image containing either a single band of elevation, measured in meters, or if there's more than one band, one named 'elevation'. Adds output bands named 'slope' and 'aspect' measured in degrees plus an unsigned byte output band named 'hillshade' for visualization. All other bands and metadata are copied from the input image. The local gradient is computed using the 4-connected neighbors of each pixel, so missing values will occur around the edges of an image.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Terrain'})
# Terrain.aspect
# Calculates aspect in degrees from a terrain DEM.  The local gradient is
# computed using the 4-connected neighbors of each pixel, so missing values
# will occur around the edges of an image.
#
# Args:
#   input: An elevation image, in meters.
signatures.append({'args': [{'description': 'An elevation image, in meters.', 'name': 'input', 'type': 'Image'}], 'description': 'Calculates aspect in degrees from a terrain DEM.\n\nThe local gradient is computed using the 4-connected neighbors of each pixel, so missing values will occur around the edges of an image.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Terrain.aspect'})
# Terrain.fillMinima
# Fills local minima.  Only works on INT types.
#
# Args:
#   image: The image to fill.
#   borderValue: The border value.
#   neighborhood: The size of the neighborhood to compute
#       over.
signatures.append({'args': [{'description': 'The image to fill.', 'name': 'image', 'type': 'Image'}, {'default': None, 'description': 'The border value.', 'name': 'borderValue', 'optional': True, 'type': 'Long'}, {'default': 50, 'description': 'The size of the neighborhood to compute over.', 'name': 'neighborhood', 'optional': True, 'type': 'Integer'}], 'description': 'Fills local minima.  Only works on INT types.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Terrain.fillMinima'})
# Terrain.hillShadow
# Creates a shadow band, with output 1 where pixels are illumunated and 0
# where they are shadowed. Takes as input an elevation band, azimuth and
# zenith of the light source in degrees, a neighborhood size, and whether or
# not to apply hysteresis when a shadow appears. Currently, this algorithm
# only works for Mercator projections, in which light rays are parallel.
#
# Args:
#   image: The image to which to apply the shadow algorithm, in
#       whicheach pixel should represent an elevation in meters.
#   azimuth: Azimuth in degrees.
#   zenith: Zenith in degrees.
#   neighborhoodSize: Neighborhood size.
#   hysteresis: Use hysteresis. Less physically accurate, but
#       may generate better images.
signatures.append({'args': [{'description': 'The image to which to apply the shadow algorithm, in whicheach pixel should represent an elevation in meters.', 'name': 'image', 'type': 'Image'}, {'description': 'Azimuth in degrees.', 'name': 'azimuth', 'type': 'Float'}, {'description': 'Zenith in degrees.', 'name': 'zenith', 'type': 'Float'}, {'default': 0, 'description': 'Neighborhood size.', 'name': 'neighborhoodSize', 'optional': True, 'type': 'Integer'}, {'default': False, 'description': 'Use hysteresis. Less physically accurate, but may generate better images.', 'name': 'hysteresis', 'optional': True, 'type': 'Boolean'}], 'description': 'Creates a shadow band, with output 1 where pixels are illumunated and 0 where they are shadowed. Takes as input an elevation band, azimuth and zenith of the light source in degrees, a neighborhood size, and whether or not to apply hysteresis when a shadow appears. Currently, this algorithm only works for Mercator projections, in which light rays are parallel.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Terrain.hillShadow'})
# Terrain.hillshade
# Computes a simple hillshade from a DEM.
#
# Args:
#   input: An elevation image, in meters.
#   azimuth: The illumination azimuth in degrees from north.
#   elevation: The illumination elevation in degrees.
signatures.append({'args': [{'description': 'An elevation image, in meters.', 'name': 'input', 'type': 'Image'}, {'default': 270.0, 'description': 'The illumination azimuth in degrees from north.', 'name': 'azimuth', 'optional': True, 'type': 'Float'}, {'default': 45.0, 'description': 'The illumination elevation in degrees.', 'name': 'elevation', 'optional': True, 'type': 'Float'}], 'description': 'Computes a simple hillshade from a DEM.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Terrain.hillshade'})
# Terrain.products
# Calculates slope, aspect, and a simple hillshade from a terrain DEM.
# Expects an image containing either a single band of elevation, measured in
# meters, or if there's more than one band, one named 'elevation'. Adds
# output bands named 'slope' and 'aspect' measured in degrees plus an
# unsigned byte output band named 'hillshade' for visualization. All other
# bands and metadata are copied from the input image. The local gradient is
# computed using the 4-connected neighbors of each pixel, so missing values
# will occur around the edges of an image.
#
# Args:
#   input: An elevation image, in meters.
signatures.append({'args': [{'description': 'An elevation image, in meters.', 'name': 'input', 'type': 'Image'}], 'description': "Calculates slope, aspect, and a simple hillshade from a terrain DEM.\n\nExpects an image containing either a single band of elevation, measured in meters, or if there's more than one band, one named 'elevation'. Adds output bands named 'slope' and 'aspect' measured in degrees plus an unsigned byte output band named 'hillshade' for visualization. All other bands and metadata are copied from the input image. The local gradient is computed using the 4-connected neighbors of each pixel, so missing values will occur around the edges of an image.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Terrain.products'})
# Terrain.slope
# Calculates slope in degrees from a terrain DEM.  The local gradient is
# computed using the 4-connected neighbors of each pixel, so missing values
# will occur around the edges of an image.
#
# Args:
#   input: An elevation image, in meters.
signatures.append({'args': [{'description': 'An elevation image, in meters.', 'name': 'input', 'type': 'Image'}], 'description': 'Calculates slope in degrees from a terrain DEM.\n\nThe local gradient is computed using the 4-connected neighbors of each pixel, so missing values will occur around the edges of an image.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Terrain.slope'})
# Test.Clustering.BerkeleySegmentation
# Performs region merging image segmentation. Initially, each pixel is its
# own segment. Over a series of iterations, adjacent segments with sufficient
# criteria are merged. Merging criteria is determined by user specified
# parameters. The output image will have a segment label band and bands
# corresponding to each of the input bands with the spectral mean for each
# segment.
#
# Args:
#   image: The image to segment.
#   numIterations: Number of iterations, also known as scale
#       parameter: The number of iterations determines how
#       strict of a threshold is enforced with respect to
#       spectral and shape properties in allowing merging.
#       Successive iterations allow for merges with
#       increasingly poor merge criteria up to the final
#       threshold, determined by the number of iterations.
#       Thus, a large number of iterations will generate few
#       large segments while a small number of iterations
#       will generate many small segments.
#   shape: Shape parameter: The shape parameter determines how
#       important the shape of a merged segment is relative to
#       spectral similarity. Shape and spectral parameters add to 1
#       (e.g., if you only care about spectral, put shape as 0).
#   compactness: Compactness parameter: Within the shape
#       consideration, there are two properties evaluated -
#       compactness and smoothness. Compactness can be thought
#       of as the area of an object compared to its perimeter
#       (e.g., a square has high compactness, a long and thin
#       rectangle does not). Smoothness can be thought of as
#       the perimeter of an object compared to its bounding
#       box perimeter (e.g., a square has high smoothness, an
#       amoeba-like shape would not). Compactness and
#       smoothness add to 1 (e.g., if you only care about
#       smoothness, put compactness as 0).
#   maxObjectSize: Maximum object size. Regions cannot be
#       merged across tiles iftheir length is over this
#       limit.
#   bandWeights: The weights for each band, in order of the
#       bands. This determines the spectral importance of each
#       band in merging. Defaulted to uniform band weights. If
#       band weights are specified, they will be automatically
#       normalized.
signatures.append({'args': [{'description': 'The image to segment.', 'name': 'image', 'type': 'Image'}, {'description': 'Number of iterations, also known as scale parameter: The number of iterations determines how strict of a threshold is enforced with respect to spectral and shape properties in allowing merging. Successive iterations allow for merges with increasingly poor merge criteria up to the final threshold, determined by the number of iterations. Thus, a large number of iterations will generate few large segments while a small number of iterations will generate many small segments.', 'name': 'numIterations', 'type': 'Integer'}, {'description': 'Shape parameter: The shape parameter determines how important the shape of a merged segment is relative to spectral similarity. Shape and spectral parameters add to 1 (e.g., if you only care about spectral, put shape as 0).', 'name': 'shape', 'type': 'Float'}, {'description': 'Compactness parameter: Within the shape consideration, there are two properties evaluated - compactness and smoothness. Compactness can be thought of as the area of an object compared to its perimeter (e.g., a square has high compactness, a long and thin rectangle does not). Smoothness can be thought of as the perimeter of an object compared to its bounding box perimeter (e.g., a square has high smoothness, an amoeba-like shape would not). Compactness and smoothness add to 1 (e.g., if you only care about smoothness, put compactness as 0).', 'name': 'compactness', 'type': 'Float'}, {'default': 256, 'description': 'Maximum object size. Regions cannot be merged across tiles iftheir length is over this limit.', 'name': 'maxObjectSize', 'optional': True, 'type': 'Integer'}, {'default': None, 'description': 'The weights for each band, in order of the bands. This determines the spectral importance of each band in merging. Defaulted to uniform band weights. If band weights are specified, they will be automatically normalized.', 'name': 'bandWeights', 'optional': True, 'type': 'List'}], 'description': 'Performs region merging image segmentation. Initially, each pixel is its own segment. Over a series of iterations, adjacent segments with sufficient criteria are merged. Merging criteria is determined by user specified parameters. The output image will have a segment label band and bands corresponding to each of the input bands with the spectral mean for each segment.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': True, 'name': 'Test.Clustering.BerkeleySegmentation'})
# Test.Clustering.HashedConsistency
# Perform consistent clustering across tiles by binning per-tile clustered
# labels into slots according to the cluster means. Input should be an image
# where one of the bands is named 'clusters' and represents the cluster
# labels. The remaining bands are spectral data. Works better when dealing
# with a small number of clusters. The output is an INT32 image in which each
# value is the cluster to which the pixel belongs.
#
# Args:
#   image: The input image for clustering.
#   maxObjectSize: Maximum object size.
#   binSize: Bin size for quantization.
signatures.append({'args': [{'description': 'The input image for clustering.', 'name': 'image', 'type': 'Image'}, {'default': 256, 'description': 'Maximum object size.', 'name': 'maxObjectSize', 'optional': True, 'type': 'Integer'}, {'default': 100.0, 'description': 'Bin size for quantization.', 'name': 'binSize', 'optional': True, 'type': 'Float'}], 'description': "Perform consistent clustering across tiles by binning per-tile clustered labels into slots according to the cluster means. Input should be an image where one of the bands is named 'clusters' and represents the cluster labels. The remaining bands are spectral data.\nWorks better when dealing with a small number of clusters. The output is an INT32 image in which each value is the cluster to which the pixel belongs.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': True, 'name': 'Test.Clustering.HashedConsistency'})
# Test.Clustering.InterTileRegionMerge
# Performs post-processing inter-tile region merging phase according to
# Berkeley image segmentation algorithm. Takes image that is a result of
# running tile-independent segmentation. Input image should have first band
# named 'clusters' containing segment labels. The other bands are spectral
# bands. Examines tile boundaries and merges adjacent segments across tiles
# if sufficient merging critieria is satisfied. Merging criteria is
# determined by user specified parameters indicating relative importance of
# spectral and shape properties.
#
# Args:
#   image: The input image for clustering.
#   scale: Scale parameter, also known as number of iterations: The
#       number of iterations determines how strict of a threshold is
#       enforced with respect to spectral and shape properties in
#       allowing merging. Successive iterations allow for merges
#       with increasingly poor merge criteria up to the final
#       threshold, determined by the number of iterations. For
#       inter-tile merging post-processing, the scale parameter
#       determines how strict a threshold to allow for merging
#       regions across adjacent tiles.
#   shape: Shape parameter: The shape parameter determines how
#       important the shape of a merged segment is relative to
#       spectral similarity. Shape and spectral parameters add to 1
#       (e.g., if you only care about spectral, put shape as 0).
#   compactness: Compactness parameter: Within the shape
#       consideration, there are two properties evaluated -
#       compactness and smoothness. Compactness can be thought
#       of as the area of an object compared to its perimeter
#       (e.g., a square has high compactness, a long and thin
#       rectangle does not). Smoothness can be thought of as
#       the perimeter of an object compared to its bounding
#       box perimeter (e.g., a square has high smoothness, an
#       amoeba-like shape would not). Compactness and
#       smoothness add to 1 (e.g., if you only care about
#       smoothness, put compactness as 0).
#   bandWeights: The weights for each band, in order of the
#       bands. This determines the spectral importance of each
#       band in merging. Defaulted to uniform band weights. If
#       band weights are specified, they will be automatically
#       normalized.
#   maxObjectSize: Maximum object size. Regions cannot be
#       merged across tiles iftheir length is over this
#       limit.
#   cornerCases: Whether to treat corner cases. If enabled, as
#       is by default, if a region A in the center tile is
#       determined to merge with a region B in an adjacent
#       tile (either north or west) and region B is determined
#       to merge with a region C in its adjacent tile (this is
#       the northwest tile from the center tile's
#       perspective), then both regions A and B will take on
#       the label of region C. That is, enabling this allows
#       merging between 3 tiles at corners.
signatures.append({'args': [{'description': 'The input image for clustering.', 'name': 'image', 'type': 'Image'}, {'description': 'Scale parameter, also known as number of iterations: The number of iterations determines how strict of a threshold is enforced with respect to spectral and shape properties in allowing merging. Successive iterations allow for merges with increasingly poor merge criteria up to the final threshold, determined by the number of iterations. For inter-tile merging post-processing, the scale parameter determines how strict a threshold to allow for merging regions across adjacent tiles.', 'name': 'scale', 'type': 'Integer'}, {'description': 'Shape parameter: The shape parameter determines how important the shape of a merged segment is relative to spectral similarity. Shape and spectral parameters add to 1 (e.g., if you only care about spectral, put shape as 0).', 'name': 'shape', 'type': 'Float'}, {'description': 'Compactness parameter: Within the shape consideration, there are two properties evaluated - compactness and smoothness. Compactness can be thought of as the area of an object compared to its perimeter (e.g., a square has high compactness, a long and thin rectangle does not). Smoothness can be thought of as the perimeter of an object compared to its bounding box perimeter (e.g., a square has high smoothness, an amoeba-like shape would not). Compactness and smoothness add to 1 (e.g., if you only care about smoothness, put compactness as 0).', 'name': 'compactness', 'type': 'Float'}, {'default': None, 'description': 'The weights for each band, in order of the bands. This determines the spectral importance of each band in merging. Defaulted to uniform band weights. If band weights are specified, they will be automatically normalized.', 'name': 'bandWeights', 'optional': True, 'type': 'List'}, {'default': 256, 'description': 'Maximum object size. Regions cannot be merged across tiles iftheir length is over this limit.', 'name': 'maxObjectSize', 'optional': True, 'type': 'Integer'}, {'default': True, 'description': "Whether to treat corner cases. If enabled, as is by default, if a region A in the center tile is determined to merge with a region B in an adjacent tile (either north or west) and region B is determined to merge with a region C in its adjacent tile (this is the northwest tile from the center tile's perspective), then both regions A and B will take on the label of region C. That is, enabling this allows merging between 3 tiles at corners.", 'name': 'cornerCases', 'optional': True, 'type': 'Boolean'}], 'description': "Performs post-processing inter-tile region merging phase according to Berkeley image segmentation algorithm. Takes image that is a result of running tile-independent segmentation. Input image should have first band named 'clusters' containing segment labels. The other bands are spectral bands. Examines tile boundaries and merges adjacent segments across tiles if sufficient merging critieria is satisfied. Merging criteria is determined by user specified parameters indicating relative importance of spectral and shape properties.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': True, 'name': 'Test.Clustering.InterTileRegionMerge'})
# Test.Clustering.RegionGrow
# An algorithm that performs clustering on the input image by region growing.
# It performs a flood fill like procedure based on either the euclidean or
# the cosine distance between the value of the starting growth point of the
# cluster and the neighboring points. The cluster grows until this distance
# is above the threshold; at this point, a new cluster starts to grow. The
# algorithm works independently on cells of a grid. This grid is defined by
# maxObjectSize and can be different from the tile size. Per-cell clusters
# are unrelated. A cluster that spans a cell boundary may receive two
# different labels in the two cells. The output is an INT32 image in which
# each value is the cluster to which the pixel belongs. A pixel in the output
# band is only defined (i.e. has a non-zero mask) if all the inputs are
# defined.
#
# Args:
#   image: The input image for clustering.
#   threshold: The distance threshold. As a cluster grows, a
#       distance measure is computed between the starting
#       point's value and the new point's value. If it is
#       greater than the threshold, the pixel is not included in
#       the cluster.
#   useCosine: Whether to use cosine distance instead of
#       euclidean distance.
#   secondPass: Whether to apply a second pass of clustering.
#   maxObjectSize: Maximum object size.
signatures.append({'args': [{'description': 'The input image for clustering.', 'name': 'image', 'type': 'Image'}, {'description': "The distance threshold. As a cluster grows, a distance measure is computed between the starting point's value and the new point's value. If it is greater than the threshold, the pixel is not included in the cluster.", 'name': 'threshold', 'type': 'Float'}, {'default': True, 'description': 'Whether to use cosine distance instead of euclidean distance.', 'name': 'useCosine', 'optional': True, 'type': 'Boolean'}, {'default': True, 'description': 'Whether to apply a second pass of clustering.', 'name': 'secondPass', 'optional': True, 'type': 'Boolean'}, {'default': 256, 'description': 'Maximum object size.', 'name': 'maxObjectSize', 'optional': True, 'type': 'Integer'}], 'description': 'An algorithm that performs clustering on the input image by region growing. It performs a flood fill like procedure based on either the euclidean or the cosine distance between the value of the starting growth point of the cluster and the neighboring points. The cluster grows until this distance is above the threshold; at this point, a new cluster starts to grow. The algorithm works independently on cells of a grid. This grid is defined by maxObjectSize and can be different from the tile size. Per-cell clusters are unrelated. A cluster that spans a cell boundary may receive two different labels in the two cells. The output is an INT32 image in which each value is the cluster to which the pixel belongs. A pixel in the output band is only defined (i.e. has a non-zero mask) if all the inputs are defined.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': True, 'name': 'Test.Clustering.RegionGrow'})
# Test.Clustering.SpatialConsistency
# Performs clustering on the input image in a consistent way across tiles.
# The algorithm works as follows: first, renumber the current tile clusters
# based on an offset; then, for each cluster that touches the left or the top
# edge, look at the adjacent tile and find that tile's cluster label. Assign
# this label, added to that tile's offset, to the current cluster and
# continue. Ambiguities can be resolved either by number of pixels touching
# the current pixel, or by closest mean. Corner cases can be resolved by
# looking at the northwest tile. Note that not all cases can be resolved.
# Input should be an image where one of the bands is named 'clusters' and
# represents the cluster labels. The remaining bands are spectral data. The
# output is an INT32 image in which each value is the cluster to which he
# pixel belongs.
#
# Args:
#   image: The input image for clustering.
#   maxObjectSize: Maximum object size.
#   useCentroid: Use centroid to search for corresponding
#       cluster.
#   cornerCases: Treat corner cases.
signatures.append({'args': [{'description': 'The input image for clustering.', 'name': 'image', 'type': 'Image'}, {'default': 256, 'description': 'Maximum object size.', 'name': 'maxObjectSize', 'optional': True, 'type': 'Integer'}, {'default': True, 'description': 'Use centroid to search for corresponding cluster.', 'name': 'useCentroid', 'optional': True, 'type': 'Boolean'}, {'default': True, 'description': 'Treat corner cases.', 'name': 'cornerCases', 'optional': True, 'type': 'Boolean'}], 'description': "Performs clustering on the input image in a consistent way across tiles. The algorithm works as follows: first, renumber the current tile clusters based on an offset; then, for each cluster that touches the left or the top edge, look at the adjacent tile and find that tile's cluster label. Assign this label, added to that tile's offset, to the current cluster and continue. Ambiguities can be resolved either by number of pixels touching the current pixel, or by closest mean. Corner cases can be resolved by looking at the northwest tile. Note that not all cases can be resolved.\nInput should be an image where one of the bands is named 'clusters' and represents the cluster labels. The remaining bands are spectral data.\nThe output is an INT32 image in which each value is the cluster to which he pixel belongs.", 'returns': 'Image', 'type': 'Algorithm', 'hidden': True, 'name': 'Test.Clustering.SpatialConsistency'})
# TrainFeatureClassifier.AggregationContainer
# INTERNAL
#
# Args:
#   collection
#   classifierName
#   classifierParameters
#   classifierMode
#   numSubsamples
#   bootstrapSubsampling
#   bootstrapAggregator
#   classifier
#   propertyList
#   classProperty
#   maxClass
signatures.append({'args': [{'name': 'collection', 'type': 'FeatureCollection'}, {'default': None, 'name': 'classifierName', 'optional': True, 'type': 'String'}, {'default': None, 'name': 'classifierParameters', 'optional': True, 'type': 'String'}, {'default': None, 'name': 'classifierMode', 'optional': True, 'type': 'String'}, {'default': 0, 'name': 'numSubsamples', 'optional': True, 'type': 'Integer'}, {'default': None, 'name': 'bootstrapSubsampling', 'optional': True, 'type': 'Float'}, {'default': None, 'name': 'bootstrapAggregator', 'optional': True, 'type': 'String'}, {'default': None, 'name': 'classifier', 'optional': True, 'type': 'OldClassifier'}, {'default': None, 'name': 'propertyList', 'optional': True, 'type': 'List'}, {'default': 'classification', 'name': 'classProperty', 'optional': True, 'type': 'String'}, {'default': 0, 'name': 'maxClass', 'optional': True, 'type': 'Integer'}], 'description': 'INTERNAL', 'returns': 'Image', 'type': 'Algorithm', 'hidden': True, 'name': 'TrainFeatureClassifier.AggregationContainer'})
# TrainImageClassifier.AggregationContainer
# INTERNAL
#
# Args:
#   image
#   classifierName
#   classifierParameters
#   classifierMode
#   numSubsamples
#   bootstrapSubsampling
#   bootstrapAggregator
#   classifier
#   bands
#   trainingImage
#   trainingBand
#   trainingRegion
#   trainingFeatures
#   trainingProperty
#   trainingProj
#   maxClass
#   subsampling
#   seed
signatures.append({'args': [{'name': 'image', 'type': 'Image'}, {'default': None, 'name': 'classifierName', 'optional': True, 'type': 'String'}, {'default': None, 'name': 'classifierParameters', 'optional': True, 'type': 'String'}, {'default': None, 'name': 'classifierMode', 'optional': True, 'type': 'String'}, {'default': 0, 'name': 'numSubsamples', 'optional': True, 'type': 'Integer'}, {'default': None, 'name': 'bootstrapSubsampling', 'optional': True, 'type': 'Float'}, {'default': None, 'name': 'bootstrapAggregator', 'optional': True, 'type': 'String'}, {'default': None, 'name': 'classifier', 'optional': True, 'type': 'OldClassifier'}, {'default': None, 'name': 'bands', 'optional': True, 'type': 'List'}, {'default': None, 'name': 'trainingImage', 'optional': True, 'type': 'Image'}, {'default': None, 'name': 'trainingBand', 'optional': True, 'type': 'String'}, {'default': None, 'name': 'trainingRegion', 'optional': True, 'type': 'Geometry'}, {'default': None, 'name': 'trainingFeatures', 'optional': True, 'type': 'FeatureCollection'}, {'default': None, 'name': 'trainingProperty', 'optional': True, 'type': 'String'}, {'default': None, 'name': 'trainingProj', 'optional': True, 'type': 'Projection'}, {'default': 0, 'name': 'maxClass', 'optional': True, 'type': 'Integer'}, {'default': 1.0, 'name': 'subsampling', 'optional': True, 'type': 'Float'}, {'default': 0, 'name': 'seed', 'optional': True, 'type': 'Long'}], 'description': 'INTERNAL', 'returns': 'Image', 'type': 'Algorithm', 'hidden': True, 'name': 'TrainImageClassifier.AggregationContainer'})
# TypedImageCollection.Constructor
# INTERNAL
#
# Args:
#   collection
#   bandNames
#   bandTypes
signatures.append({'args': [{'name': 'collection', 'type': 'ImageCollection'}, {'name': 'bandNames', 'type': 'List'}, {'name': 'bandTypes', 'type': 'List'}], 'description': 'INTERNAL', 'returns': 'Object', 'type': 'Algorithm', 'hidden': True, 'name': 'TypedImageCollection.Constructor'})
# Validate.AggregationContainer
# INTERNAL
#
# Args:
#   classifier
signatures.append({'args': [{'name': 'classifier', 'type': 'Classifier'}], 'description': 'INTERNAL', 'returns': 'Image', 'type': 'Algorithm', 'hidden': True, 'name': 'Validate.AggregationContainer'})
# WHRC.CombinePoints
# Averaged values of observations in a pixel if the number of  observations
# exceeds a threshold.
#
# Args:
#   collection: The collection to combine.
#   intersections: The minimum number of intersecting
#       points.
#   pixelSize: Pixel size
signatures.append({'args': [{'description': 'The collection to combine.', 'name': 'collection', 'type': 'FeatureCollection'}, {'description': 'The minimum number of intersecting points.', 'name': 'intersections', 'type': 'Integer'}, {'description': 'Pixel size', 'name': 'pixelSize', 'type': 'Float'}], 'description': 'Averaged values of observations in a pixel if the number of  observations exceeds a threshold.', 'returns': 'FeatureCollection', 'type': 'Algorithm', 'hidden': True, 'name': 'WHRC.CombinePoints'})
# Window.max
# Applies a morphological reducer() filter to each band of an image using a
# named or custom kernel.
#
# Args:
#   image: The image to which to apply the operations.
#   radius: The radius of the kernel to use.
#   kernelType: The type of kernel to use. Options include:
#       'circle', 'square', 'cross', 'plus', octagon' and
#       'diamond'.
#   units: If a kernel is not specified, this determines whether the
#       kernel is in meters or pixels.
#   iterations: The number of times to apply the given kernel.
#   kernel: A custom kernel. If used, kernelType and radius are
#       ignored.
signatures.append({'args': [{'description': 'The image to which to apply the operations.', 'name': 'image', 'type': 'Image'}, {'default': 1.5, 'description': 'The radius of the kernel to use.', 'name': 'radius', 'optional': True, 'type': 'Float'}, {'default': 'circle', 'description': "The type of kernel to use. Options include: 'circle', 'square', 'cross', 'plus', octagon' and 'diamond'.", 'name': 'kernelType', 'optional': True, 'type': 'String'}, {'default': 'pixels', 'description': 'If a kernel is not specified, this determines whether the kernel is in meters or pixels.', 'name': 'units', 'optional': True, 'type': 'String'}, {'default': 1, 'description': 'The number of times to apply the given kernel.', 'name': 'iterations', 'optional': True, 'type': 'Integer'}, {'default': None, 'description': 'A custom kernel. If used, kernelType and radius are ignored.', 'name': 'kernel', 'optional': True, 'type': 'Kernel'}], 'description': 'Applies a morphological reducer() filter to each band of an image using a named or custom kernel.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Window.max'})
# Window.mean
# Applies a morphological mean filter to each band of an image using a named
# or custom kernel.
#
# Args:
#   image: The image to which to apply the operations.
#   radius: The radius of the kernel to use.
#   kernelType: The type of kernel to use. Options include:
#       'circle', 'square', 'cross', 'plus', octagon' and
#       'diamond'.
#   units: If a kernel is not specified, this determines whether the
#       kernel is in meters or pixels.
#   iterations: The number of times to apply the given kernel.
#   kernel: A custom kernel. If used, kernelType and radius are
#       ignored.
signatures.append({'args': [{'description': 'The image to which to apply the operations.', 'name': 'image', 'type': 'Image'}, {'default': 1.5, 'description': 'The radius of the kernel to use.', 'name': 'radius', 'optional': True, 'type': 'Float'}, {'default': 'circle', 'description': "The type of kernel to use. Options include: 'circle', 'square', 'cross', 'plus', octagon' and 'diamond'.", 'name': 'kernelType', 'optional': True, 'type': 'String'}, {'default': 'pixels', 'description': 'If a kernel is not specified, this determines whether the kernel is in meters or pixels.', 'name': 'units', 'optional': True, 'type': 'String'}, {'default': 1, 'description': 'The number of times to apply the given kernel.', 'name': 'iterations', 'optional': True, 'type': 'Integer'}, {'default': None, 'description': 'A custom kernel. If used, kernelType and radius are ignored.', 'name': 'kernel', 'optional': True, 'type': 'Kernel'}], 'description': 'Applies a morphological mean filter to each band of an image using a named or custom kernel.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Window.mean'})
# Window.median
# Applies a morphological reducer() filter to each band of an image using a
# named or custom kernel.
#
# Args:
#   image: The image to which to apply the operations.
#   radius: The radius of the kernel to use.
#   kernelType: The type of kernel to use. Options include:
#       'circle', 'square', 'cross', 'plus', octagon' and
#       'diamond'.
#   units: If a kernel is not specified, this determines whether the
#       kernel is in meters or pixels.
#   iterations: The number of times to apply the given kernel.
#   kernel: A custom kernel. If used, kernelType and radius are
#       ignored.
signatures.append({'args': [{'description': 'The image to which to apply the operations.', 'name': 'image', 'type': 'Image'}, {'default': 1.5, 'description': 'The radius of the kernel to use.', 'name': 'radius', 'optional': True, 'type': 'Float'}, {'default': 'circle', 'description': "The type of kernel to use. Options include: 'circle', 'square', 'cross', 'plus', octagon' and 'diamond'.", 'name': 'kernelType', 'optional': True, 'type': 'String'}, {'default': 'pixels', 'description': 'If a kernel is not specified, this determines whether the kernel is in meters or pixels.', 'name': 'units', 'optional': True, 'type': 'String'}, {'default': 1, 'description': 'The number of times to apply the given kernel.', 'name': 'iterations', 'optional': True, 'type': 'Integer'}, {'default': None, 'description': 'A custom kernel. If used, kernelType and radius are ignored.', 'name': 'kernel', 'optional': True, 'type': 'Kernel'}], 'description': 'Applies a morphological reducer() filter to each band of an image using a named or custom kernel.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Window.median'})
# Window.min
# Applies a morphological reducer() filter to each band of an image using a
# named or custom kernel.
#
# Args:
#   image: The image to which to apply the operations.
#   radius: The radius of the kernel to use.
#   kernelType: The type of kernel to use. Options include:
#       'circle', 'square', 'cross', 'plus', octagon' and
#       'diamond'.
#   units: If a kernel is not specified, this determines whether the
#       kernel is in meters or pixels.
#   iterations: The number of times to apply the given kernel.
#   kernel: A custom kernel. If used, kernelType and radius are
#       ignored.
signatures.append({'args': [{'description': 'The image to which to apply the operations.', 'name': 'image', 'type': 'Image'}, {'default': 1.5, 'description': 'The radius of the kernel to use.', 'name': 'radius', 'optional': True, 'type': 'Float'}, {'default': 'circle', 'description': "The type of kernel to use. Options include: 'circle', 'square', 'cross', 'plus', octagon' and 'diamond'.", 'name': 'kernelType', 'optional': True, 'type': 'String'}, {'default': 'pixels', 'description': 'If a kernel is not specified, this determines whether the kernel is in meters or pixels.', 'name': 'units', 'optional': True, 'type': 'String'}, {'default': 1, 'description': 'The number of times to apply the given kernel.', 'name': 'iterations', 'optional': True, 'type': 'Integer'}, {'default': None, 'description': 'A custom kernel. If used, kernelType and radius are ignored.', 'name': 'kernel', 'optional': True, 'type': 'Kernel'}], 'description': 'Applies a morphological reducer() filter to each band of an image using a named or custom kernel.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Window.min'})
# Window.mode
# Applies a morphological reducer() filter to each band of an image using a
# named or custom kernel.
#
# Args:
#   image: The image to which to apply the operations.
#   radius: The radius of the kernel to use.
#   kernelType: The type of kernel to use. Options include:
#       'circle', 'square', 'cross', 'plus', octagon' and
#       'diamond'.
#   units: If a kernel is not specified, this determines whether the
#       kernel is in meters or pixels.
#   iterations: The number of times to apply the given kernel.
#   kernel: A custom kernel. If used, kernelType and radius are
#       ignored.
signatures.append({'args': [{'description': 'The image to which to apply the operations.', 'name': 'image', 'type': 'Image'}, {'default': 1.5, 'description': 'The radius of the kernel to use.', 'name': 'radius', 'optional': True, 'type': 'Float'}, {'default': 'circle', 'description': "The type of kernel to use. Options include: 'circle', 'square', 'cross', 'plus', octagon' and 'diamond'.", 'name': 'kernelType', 'optional': True, 'type': 'String'}, {'default': 'pixels', 'description': 'If a kernel is not specified, this determines whether the kernel is in meters or pixels.', 'name': 'units', 'optional': True, 'type': 'String'}, {'default': 1, 'description': 'The number of times to apply the given kernel.', 'name': 'iterations', 'optional': True, 'type': 'Integer'}, {'default': None, 'description': 'A custom kernel. If used, kernelType and radius are ignored.', 'name': 'kernel', 'optional': True, 'type': 'Kernel'}], 'description': 'Applies a morphological reducer() filter to each band of an image using a named or custom kernel.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'Window.mode'})
# WrappedFeatureCollection.AggregationContainer
# INTERNAL
#
# Args:
#   collection
signatures.append({'args': [{'name': 'collection', 'type': 'FeatureCollection'}], 'description': 'INTERNAL', 'returns': 'Image', 'type': 'Algorithm', 'hidden': True, 'name': 'WrappedFeatureCollection.AggregationContainer'})
# green_mosaic/com.google.earthengine.examples.greenmosaic.GreenMosaic
# Mosaicks an MCD43A4 image collection by taking the top fraction graded by
# NDVI, then selecting the geometric mediod.
#
# Args:
#   inputs: The MCD43A4 collection to mosaic.
#   ndviStartPercentile
#   ndviEndPercentile
signatures.append({'args': [{'description': 'The MCD43A4 collection to mosaic.', 'name': 'inputs', 'type': 'ImageCollection'}, {'name': 'ndviStartPercentile', 'type': 'Float'}, {'name': 'ndviEndPercentile', 'type': 'Float'}], 'description': 'Mosaicks an MCD43A4 image collection by taking the top fraction graded by NDVI, then selecting the geometric mediod.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': True, 'name': 'green_mosaic/com.google.earthengine.examples.greenmosaic.GreenMosaic'})
# reduce.and
# Reduces an image collection by setting each pixel to 1 iff all the non-
# masked values at that pixel are non-zero across the stack of all matching
# bands. Bands are matched by name.
#
# Args:
#   collection: The image collection to reduce.
signatures.append({'args': [{'description': 'The image collection to reduce.', 'name': 'collection', 'type': 'ImageCollection'}], 'description': 'Reduces an image collection by setting each pixel to 1 iff all the non-masked values at that pixel are non-zero across the stack of all matching bands. Bands are matched by name.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'reduce.and'})
# reduce.count
# Reduces an image collection by calculating the number of images with a
# valid mask at each pixel across the stack of all matching bands. Bands are
# matched by name.
#
# Args:
#   collection: The image collection to reduce.
signatures.append({'args': [{'description': 'The image collection to reduce.', 'name': 'collection', 'type': 'ImageCollection'}], 'description': 'Reduces an image collection by calculating the number of images with a valid mask at each pixel across the stack of all matching bands. Bands are matched by name.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'reduce.count'})
# reduce.max
# Reduces an image collection by calculating the maximum value of each pixel
# across the stack of all matching bands. Bands are matched by name.
#
# Args:
#   collection: The image collection to reduce.
signatures.append({'args': [{'description': 'The image collection to reduce.', 'name': 'collection', 'type': 'ImageCollection'}], 'description': 'Reduces an image collection by calculating the maximum value of each pixel across the stack of all matching bands. Bands are matched by name.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'reduce.max'})
# reduce.mean
# Reduces an image collection by calculating the mean of all values at each
# pixel across the stack of all matching bands. Bands are matched by name.
#
# Args:
#   collection: The image collection to reduce.
signatures.append({'args': [{'description': 'The image collection to reduce.', 'name': 'collection', 'type': 'ImageCollection'}], 'description': 'Reduces an image collection by calculating the mean of all values at each pixel across the stack of all matching bands. Bands are matched by name.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'reduce.mean'})
# reduce.median
# Reduces an image collection by calculating the median of all values at each
# pixel across the stack of all matching bands. Bands are matched by name.
#
# Args:
#   collection: The image collection to reduce.
signatures.append({'args': [{'description': 'The image collection to reduce.', 'name': 'collection', 'type': 'ImageCollection'}], 'description': 'Reduces an image collection by calculating the median of all values at each pixel across the stack of all matching bands. Bands are matched by name.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'reduce.median'})
# reduce.min
# Reduces an image collection by calculating the minimum value of each pixel
# across the stack of all matching bands. Bands are matched by name.
#
# Args:
#   collection: The image collection to reduce.
signatures.append({'args': [{'description': 'The image collection to reduce.', 'name': 'collection', 'type': 'ImageCollection'}], 'description': 'Reduces an image collection by calculating the minimum value of each pixel across the stack of all matching bands. Bands are matched by name.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'reduce.min'})
# reduce.mode
# Reduces an image collection by calculating the most common value at each
# pixel across the stack of all matching bands. Bands are matched by name.
#
# Args:
#   collection: The image collection to reduce.
signatures.append({'args': [{'description': 'The image collection to reduce.', 'name': 'collection', 'type': 'ImageCollection'}], 'description': 'Reduces an image collection by calculating the most common value at each pixel across the stack of all matching bands. Bands are matched by name.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'reduce.mode'})
# reduce.or
# Reduces an image collection by setting each pixel to 1 iff any of the non-
# masked values at that pixel are non-zero across the stack of all matching
# bands. Bands are matched by name.
#
# Args:
#   collection: The image collection to reduce.
signatures.append({'args': [{'description': 'The image collection to reduce.', 'name': 'collection', 'type': 'ImageCollection'}], 'description': 'Reduces an image collection by setting each pixel to 1 iff any of the non-masked values at that pixel are non-zero across the stack of all matching bands. Bands are matched by name.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'reduce.or'})
# reduce.product
# Reduces an image collection by calculating the product of all values at
# each pixel across the stack of all matching bands. Bands are matched by
# name.
#
# Args:
#   collection: The image collection to reduce.
signatures.append({'args': [{'description': 'The image collection to reduce.', 'name': 'collection', 'type': 'ImageCollection'}], 'description': 'Reduces an image collection by calculating the product of all values at each pixel across the stack of all matching bands. Bands are matched by name.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'reduce.product'})
# reduce.sum
# Reduces an image collection by calculating the sum of all values at each
# pixel across the stack of all matching bands. Bands are matched by name.
#
# Args:
#   collection: The image collection to reduce.
signatures.append({'args': [{'description': 'The image collection to reduce.', 'name': 'collection', 'type': 'ImageCollection'}], 'description': 'Reduces an image collection by calculating the sum of all values at each pixel across the stack of all matching bands. Bands are matched by name.', 'returns': 'Image', 'type': 'Algorithm', 'hidden': False, 'name': 'reduce.sum'})
