import { OrderingOption, Orderings } from "../Datas"

export default function SortSelector({
	values,
	onSelect
}: {
	values: OrderingOption[]
	onSelect: (selected: Orderings) => void
}) {

	function onSelectChange(e: React.ChangeEvent<HTMLSelectElement>) {
		onSelect(Orderings[e.target.value as keyof typeof Orderings])
	}

	return (
		<div>
			<select className='rounded-lg p-2 
				bg-transparent 
				border border-gray-500 
				text-gray-200'
					
				defaultValue={values[0].value}
				onChange={onSelectChange}>
				{
					values.map((o) =>
						<option
							key={o.value}
							value={o.value}>

							{o.displayName}
						</option>
					)
				}
			</select>
		</div>
	)
}